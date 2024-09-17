from uuid import uuid4

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, filters, MessageHandler, \
    CommandHandler

from bin.menu import menu
from lib.filters import trade_button_filter
from lib.init import TRADES_COLLECTION
from lib.keyboard_markup import generate_collection_keyboard

from lib.classes.user import User


async def trade_initialization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user = User.get(telegram_user)
    # TRADES_COLLECTION.insert_one({"id": uuid4().hex[-8:],
    #                               "sender": user.id,
    #                               "receiver: "})
    # reply_markup = generate_collection_keyboard(update, context, user.id, page=0, in_market=False, trade=True)
    # await update.message.reply_text("Выберите карты для обмена или нажмите /trade_cancel для отмены:",
    #                                 reply_markup=reply_markup)  # ERROR-IGNORE
    await update.message.reply_text("Введите ID пользователя, с которым хотите совершить обмен")
    return "trade_init"


async def trade_handle(update: Update, _: ContextTypes.DEFAULT_TYPE):
    try:
        receiver_id = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Неверный ввод")
        return "trade_init"

    if not User.get(user=None, update=int(receiver_id)):
        await update.message.reply_text("Пользователя с таким ID не существует. Проверьте данные и повторите ввод.")
        return "trade_init"

    telegram_user = update.effective_user
    user = User.get(telegram_user)


trade_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(trade_button_filter, trade_initialization)],
    states={
        "trade_init": [MessageHandler(filters.TEXT & ~filters.COMMAND, )],
    },
    fallbacks=[CommandHandler("cancel", menu)]
)
