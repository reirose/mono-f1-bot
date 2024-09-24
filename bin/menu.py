import datetime

from telegram import Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import main_menu_markup


async def menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    cards_n = len(user.collection)
    unique_cards_n = len(list(set(user.collection)))

    response = (f"<b>{user.username} • {user.id}</b>\n\n"
                f"Карт в коллекции: {cards_n}\n"
                f"<i>из которых уникальные: {unique_cards_n}</i>\n"
                f"Монет: {user.coins} 🪙")

    await mes.reply_text(response,
                         reply_markup=main_menu_markup,
                         parse_mode="HTML")


async def about_me(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    mes = update.message

    days_in_game = int((datetime.datetime.now().timestamp() - user.date_of_registration) // 86400) + 1

    packs_opened = user.statistics["packs_opened"]
    coins_spent = user.statistics["coins_spent"]
    trades_complete = user.statistics["trades_complete"]

    response = (f"<b>{user.username} • {user.id}</b>\n\n"
                f"Паков открыто: {packs_opened}\n"
                f"Монет потрачено: {coins_spent} 🪙\n"
                f"Совершено обменов: {trades_complete}\n"
                f"Дней в игре: {days_in_game}")

    await mes.reply_text(response,
                         reply_markup=main_menu_markup,
                         parse_mode="HTML")
