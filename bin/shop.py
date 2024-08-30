from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import shop_inline_markup


async def shop_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    response = ("Тут можно приобрести дополнительные паки для открытия.\n\n"
                f"Ваши монеты: {user.coins} шт.")
    reply_markup = shop_inline_markup

    await mes.reply_text(response,
                         reply_markup=reply_markup)
