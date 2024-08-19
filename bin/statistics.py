from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import main_menu_markup


async def statistics(update: Update, _: ContextTypes.DEFAULT_TYPE):
    telegram_user = update.effective_user
    user = User.get(telegram_user)
    mes = update.message

    response: str = ("📊 Ваша статистика:\n\n"
                     f"Получено карт: {len(user.collection)}\n"
                     f"Доступно круток: {user.rolls_available}")

    await mes.reply_text(response,
                         reply_markup=main_menu_markup)
