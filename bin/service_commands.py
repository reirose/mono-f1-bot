from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User

from lib.keyboard_markup import main_menu_markup


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mes = update.message

    user_data = User.get(user)

    await mes.reply_text(text="Добро пожаловать, снова!",
                         reply_markup=main_menu_markup)
