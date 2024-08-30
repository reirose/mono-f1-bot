from telegram import Update
from telegram.ext import ContextTypes

from lib.keyboard_markup import other_menu_markup


async def other_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text="Выберите раздел",
                                   chat_id=update.effective_user.id,
                                   reply_markup=other_menu_markup)
