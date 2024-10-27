import random
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from lib.classes.user import User
from lib.filters import coinflip_button_filter
from lib.keyboard_markup import coinflip_menu_markup


async def coinflip_menu(update: Update, __: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎮", reply_markup=coinflip_menu_markup)


async def coinflip_entry(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.message.from_user)
    if not user.coins:
        await update.message.reply_text("У вас совсем не осталось монет.\n\n<i>Какой-то невнятный бубнёж про кружку "
                                        "пива...</i>", parse_mode="HTML")
        return ConversationHandler.END

    if user.coinflip:
        await update.message.reply_text("У вас есть незаконченная игра! Если вы хотите отозвать предложение - нажмите "
                                        "/cancel", parse_mode="HTML")
        return ConversationHandler.END

    await update.message.reply_text("Введите имя или ID пользователя, с которым хотите сыграть\n(вы можете прервать "
                                    "операцию командой /cancel)")
    return "coinflip_parse_id"


async def coinflip_parse_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    try:
        receiver_id = int(mes.text)
    except ValueError:
        receiver_id = mes.text

    if receiver_id == mes.from_user.id or receiver_id == mes.from_user.username:
        await mes.reply_text("Неверный ввод")
        return "coinflip_parse_id"

    receiver = User.get(user=None, update=receiver_id)
    if not receiver:
        await mes.reply_text("Пользователя с таким ID или именем не существует. Проверьте данные и повторите ввод.")
        return "coinflip_parse_id"

    if not receiver.coins:
        await mes.reply_text("У пользователя нет монет. Попробуйте сыграть с кем-то другим!(вы можете прервать "
                             "операцию командой /cancel)")
        return "coinflip_parse_id"

    if receiver.coinflip:
        await mes.reply_text("Пользователь уже в игре! Попробуйте сыграть с кем-то другим!(вы можете прервать "
                             "операцию командой /coinflip_abort)")
        return "coinflip_parse_id"

    bet_cap = min(User.get(mes.from_user).coins, receiver.coins)
    context.user_data["bet_cap"] = bet_cap
    context.user_data["receiver_id"] = receiver.id

    await mes.reply_text(f"Введите вашу ставку (максимум: {bet_cap})")
    return "coinflip_bet_handle"


async def coinflip_bet_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    bet_cap = context.user_data["bet_cap"]
    receiver_id = context.user_data["receiver_id"]

    try:
        bet = int(mes.text)
    except ValueError:
        await mes.reply_text("Неверный ввод")
        return "coinflip_bet_handle"

    if bet > bet_cap:
        await mes.reply_text("Неверный ввод")
        return "coinflip_bet_handle"

    user = User.get(mes.from_user)
    user.coinflip = 1
    user.write()

    resp = "Предложение сыграть отправлено, ждём подтверждения."
    resp_rec = f"@{mes.from_user.username} предложил сыграть в \"монетку\" на {bet} 🪙"
    resp_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Принять", callback_data=f"coinflip_accept_{mes.from_user.id}_{bet}")],
        [InlineKeyboardButton("Отклонить", callback_data=f"coinflip_decline_{mes.from_user.id}")]
    ])

    sent = await context.bot.send_message(chat_id=receiver_id, text=resp_rec, reply_markup=resp_keyboard)

    abort_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Отменить", callback_data=f"coinflip_cancel_{receiver_id}_{sent.message_id}")]
    ])
    await context.bot.send_message(chat_id=mes.from_user.id, text=resp, reply_markup=abort_keyboard)

    return ConversationHandler.END


async def cancel(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


async def abort(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.message.from_user)
    user.coinflip = 0
    user.write()

    await update.message.reply_text("Успешно!")
    return coinflip_conv_handler.END


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

    await context.bot.send_message(chat_id=winner.id, text=resp_winner, parse_mode="HTML")
    await context.bot.send_message(chat_id=loser.id, text=resp_loser, parse_mode="HTML")


coinflip_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(coinflip_button_filter, coinflip_entry)],
    states={
        "coinflip_parse_id": [MessageHandler(filters.TEXT & ~filters.COMMAND, coinflip_parse_id)],
        "coinflip_bet_handle": [MessageHandler(filters.TEXT & ~filters.COMMAND, coinflip_bet_handle)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    allow_reentry=True  # This will allow canceling at any point
)
