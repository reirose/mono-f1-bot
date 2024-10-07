from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, filters, MessageHandler, CommandHandler

from bin.collection import collection_menu
from lib.filters import trade_button_filter
from lib.keyboard_markup import generate_collection_keyboard

from lib.classes.user import User


async def trade_initialization(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите ID или имя пользователя, с которым хотите совершить обмен "
                                    "(для отмены нажмите /cancel)")
    return "trade_init"


async def trade_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    try:
        receiver_id = int(update.message.text)
    except ValueError:
        receiver_id = update.message.text

    if receiver_id == mes.from_user.id or receiver_id == mes.from_user.username:
        await update.message.reply_text("Неверный ввод")
        return "trade_init"

    if not User.get(user=None, update=receiver_id):
        await update.message.reply_text("Пользователя с таким ID или именем не существует. "
                                        "Проверьте данные и повторите ввод.")
        return "trade_init"

    telegram_user = update.effective_user
    user = User.get(telegram_user)
    keyboard = await generate_collection_keyboard(update, context, telegram_user_id=user.id,
                                                  page=0, in_market=False, trade=True, trade_receiver=receiver_id)
    await mes.reply_text("Выберите карты для обмена",
                         reply_markup=keyboard)
    return ConversationHandler.END


async def cancel_trade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await collection_menu(update, context)
    return ConversationHandler.END


trade_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(trade_button_filter, trade_initialization)],
    states={
        "trade_init": [MessageHandler(filters.TEXT & ~filters.COMMAND, trade_handle)],
    },
    fallbacks=[CommandHandler("cancel", cancel_trade)]
)
