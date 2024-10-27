import random

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from lib.classes.user import User
from lib.filters import coinflip_pve_button_filter
from lib.keyboard_markup import coinflip_menu_markup


async def bot_coinflip_menu(update: Update, __: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите режим игры",
                                    reply_markup=coinflip_menu_markup)


async def bot_coinflip_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
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

    bet_cap = User.get(mes.from_user).coins
    context.user_data["bet_cap"] = bet_cap

    await mes.reply_text("Введите вашу ставку (максимум: %i)" % bet_cap)

    return "bot_coinflip_bet_handle"


async def bot_coinflip_bet_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    bet_cap = context.user_data["bet_cap"]
    try:
        bet = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Неверный ввод")
        return "bot_coinflip_bet_handle"

    if bet > bet_cap:
        await update.message.reply_text("Неверный ввод")
        return "bot_coinflip_bet_handle"

    user = User.get(mes.from_user)
    user.coinflip = bet
    user.write()

    await context.bot.send_message(chat_id=mes.from_user.id,
                                   text="🪙")

    context.job_queue.run_once(bot_coinflip_result_handle, 3.5, data=[user.id])

    return ConversationHandler.END


async def bot_coinflip_result_handle(context: ContextTypes.DEFAULT_TYPE):
    user = User.get(None, context.job.data[0])
    winner = random.choice(['bot', user.id])
    bet = user.coinflip
    user.coinflip = 0
    if winner == 'bot':
        user.coins -= bet
        user.write()
        resp = "Бот победил!\n<i>Списано: %i 🪙 (Всего: %i 🪙)</i>" % (bet, user.coins)
        await context.bot.send_message(chat_id=user.id,
                                       text=resp,
                                       parse_mode="HTML")
        return

    user.coins += bet
    user.write()

    resp = "Вы победили!\n<i>Начислено: %i 🪙 (Всего: %i 🪙)</i>" % (bet, user.coins)
    await context.bot.send_message(chat_id=user.id,
                                   text=resp,
                                   parse_mode="HTML")


async def bot_cancel(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


bot_coinflip_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(coinflip_pve_button_filter, bot_coinflip_entry)],
    states={
        "bot_coinflip_bet_handle": [MessageHandler(filters.TEXT & ~filters.COMMAND, bot_coinflip_bet_handle)],
    },
    fallbacks=[CommandHandler("cancel", bot_cancel)],
    allow_reentry=True  # This will allow canceling at any point
)
