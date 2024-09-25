import random
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from lib.classes.user import User
from lib.filters import coinflip_button_filter
from lib.keyboard_markup import coinflip_menu_markup


async def coinflip_menu(update: Update, __: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите режим игры",
                                    reply_markup=coinflip_menu_markup)


async def coinflip_entry(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not User.get(update.message.from_user).coins:
        await update.message.reply_text("У вас совсем не осталось монет."
                                        "\n\n<i>Какой-то невнятный бубнёж про кружку пива...</i>",
                                        parse_mode="HTML")
        return ConversationHandler.END

    if User.get(update.message.from_user).coinflip:
        await update.message.reply_text("У вас есть незаконченная игра! Если вы хотите отозвать предложение - "
                                        "нажмите /coinflip_cancel",
                                        parse_mode="HTML")
        return ConversationHandler.END

    await update.message.reply_text("Введите имя или ID пользователя, с которым хотите сыграть\n"
                                    "(вы можете прервать операцию командой /coinflip_abort)")
    return "coinflip_parse_id"


async def coinflip_parse_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    try:
        receiver_id = int(update.message.text)
    except ValueError:
        receiver_id = update.message.text

    if receiver_id == mes.from_user.id or receiver_id == mes.from_user.username:
        await update.message.reply_text("Неверный ввод")
        return "coinflip_parse_id"

    if not User.get(user=None, update=receiver_id):
        await update.message.reply_text("Пользователя с таким ID или именем не существует. "
                                        "Проверьте данные и повторите ввод.")
        return "coinflip_parse_id"

    if not User.get(user=None, update=receiver_id).coins:
        await update.message.reply_text("У пользователя нет монет. Попробуйте сыграть с кем-то другим!"
                                        "(вы можете прервать операцию командой /coinflip_abort)")
        return "coinflip_parse_id"

    if User.get(user=None, update=receiver_id).coinflip:
        await update.message.reply_text("Пользователь уже в игре! Попробуйте сыграть с кем-то другим!"
                                        "(вы можете прервать операцию командой /coinflip_abort)")
        return "coinflip_parse_id"

    bet_cap = min([User.get(user=None, update=receiver_id).coins, User.get(mes.from_user).coins])
    context.user_data["bet_cap"] = bet_cap
    context.user_data["receiver_id"] = User.get(None, receiver_id).id

    await mes.reply_text("Введите вашу ставку (максимум: %i)" % bet_cap)

    return "coinflip_bet_handle"


async def coinflip_bet_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    bet_cap = context.user_data["bet_cap"]
    receiver_id = context.user_data["receiver_id"]
    try:
        bet = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Неверный ввод")
        return "coinflip_bet_handle"

    if bet > bet_cap:
        await update.message.reply_text("Неверный ввод")
        return "coinflip_bet_handle"

    user = User.get(mes.from_user)
    user.coinflip = 1
    user.write()

    resp = "Предложение сыграть отправлено, ждём подтверждения."
    resp_rec = "@%s предложил сыграть в \"монетку\" на %i 🪙" % (mes.from_user.username, bet)
    resp_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Принять",
                                                                callback_data=f"coinflip_accept_"
                                                                              f"{mes.from_user.id}_{bet}")],
                                          [InlineKeyboardButton("Отклонить",
                                                                callback_data=f"coinflip_decline_{mes.from_user.id}")]])

    sent = await context.bot.send_message(chat_id=receiver_id,
                                          text=resp_rec,
                                          reply_markup=resp_keyboard)

    abort_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отменить",
                                                                 callback_data=f"coinflip_cancel_{receiver_id}"
                                                                               f"_{sent.message_id}")]])
    await context.bot.send_message(chat_id=mes.from_user.id,
                                   text=resp,
                                   reply_markup=abort_keyboard)

    return ConversationHandler.END


async def cancel(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


async def abort(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.message.from_user)
    user.coinflip = 0
    user.write()

    await update.message.reply_text("Успешно!")


async def coinflip_result(context: ContextTypes.DEFAULT_TYPE):
    query_data = context.job.data[0]["query_data"]
    user_id = context.job.data[0]["user_id"]
    p1 = int(re.search("coinflip_accept_(.+)_(.+)", query_data).group(1))
    p2 = user_id

    winner = User.get(None, random.choice([p1, p2]))
    loser = p1 if winner.id == p2 else p2
    loser = User.get(None, loser)

    bet = int(re.search("coinflip_accept_(.+)_(.+)", query_data).group(2))

    resp_winner = f"Вы победили!\n<i>Баланс пополнен на {bet} 🪙 (Всего: {winner.coins + bet} 🪙)</i>"
    resp_loser = f"{winner.username} победил!\n<i>Списано {bet} 🪙 (Всего: {loser.coins - bet} 🪙)</i>"

    winner.coins += bet
    winner.coinflip = 0
    loser.coins -= bet
    if loser.coins < 0:
        loser.coins = 0
    loser.coinflip = 0

    winner.write()
    loser.write()

    await context.bot.send_message(chat_id=winner.id,
                                   text=resp_winner,
                                   parse_mode="HTML")

    await context.bot.send_message(chat_id=loser.id,
                                   text=resp_loser,
                                   parse_mode="HTML")


coinflip_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(coinflip_button_filter, coinflip_entry)],
    states={
        "coinflip_parse_id": [MessageHandler(filters.TEXT & ~filters.COMMAND, coinflip_parse_id)],
        "coinflip_bet_handle": [MessageHandler(filters.TEXT & ~filters.COMMAND, coinflip_bet_handle)],
    },
    fallbacks=[CommandHandler("coinflip_abort", cancel)]
)
