from telegram import Update
from telegram.ext import ContextTypes

from bin.menu import menu
from lib.classes.user import User
from lib.filters import DEV_MODE
from lib.keyboard_markup import main_menu_markup


async def dev_mode_change(_: Update, __: ContextTypes.DEFAULT_TYPE):
    DEV_MODE.change()


async def unstuck(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    user.status = "idle"
    user.write()
    await menu(update, _)


async def start(update: Update, _: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    mes = update.message

    User.get(telegram_user)

    await mes.reply_text(text="Добро пожаловать, снова!",
                         reply_markup=main_menu_markup)

    await menu(update, _)
