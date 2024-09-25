from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters, CommandHandler

from bin.other import other_menu
from lib.classes.user import User
from lib.filters import coinflip_button_filter


async def coinflip_entry(update: Update, _: ContextTypes.DEFAULT_TYPE):
    if not User.get(update.message.from_user).coins:
        await update.message.reply_text("У вас совсем не осталось монет."
                                        "\n\n<i>Какой-то невнятный бубнёж про кружку пива...</i>",
                                        parse_mode="HTML")
        return ConversationHandler.END
    await update.message.reply_text("Введите имя или ID пользователя, с которым хотите сыграть\n"
                                    "(вы можете прервать операцию командой /coinflip_cancel)")
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

    print(receiver_id)
    print(User.get(user=None, update=receiver_id).username)

    if not User.get(user=None, update=receiver_id).coins:
        await update.message.reply_text("У пользователя нет монет. Попробуйте сыграть с кем-то другим!"
                                        "(вы можете прервать операцию командой /coinflip_cancel)")
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
    user.coinflip = bet
    user.write()

    resp = "Предложение сыграть отправлено, ждём подтверждения."
    resp_rec = "@%s предложил сыграть в \"монетку\" на %i 🪙" % (mes.from_user.username, bet)
    resp_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Принять",
                                                                callback_data=f"coinflip_accept_{mes.from_user.id}")],
                                          [InlineKeyboardButton("Отклонить",
                                                                callback_data=f"coinflip_decline_{mes.from_user.id}")]])

    await context.bot.send_message(chat_id=mes.from_user.id,
                                   text=resp)
    await context.bot.send_message(chat_id=receiver_id,
                                   text=resp_rec,
                                   reply_markup=resp_keyboard)

    return ConversationHandler.END


async def cancel(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Действие отменено.")
    return ConversationHandler.END


coinflip_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(coinflip_button_filter, coinflip_entry)],
    states={
        "coinflip_parse_id": [MessageHandler(filters.TEXT & ~filters.COMMAND, coinflip_parse_id)],
        "coinflip_bet_handle": [MessageHandler(filters.TEXT & ~filters.COMMAND, coinflip_bet_handle)],
    },
    fallbacks=[CommandHandler("coinflip_cancel", cancel)]
)
