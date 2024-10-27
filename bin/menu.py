import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bin.achievements import bot_check_achievements
from lib.classes.user import User
from lib.keyboard_markup import main_menu_markup
from lib.variables import achievements_dict, roll_cards_dict


async def menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)
    if not User.get(update.effective_user):
        return

    cards_n = len(user.collection)
    unique_cards_n = len(list(set(user.collection)))

    collectors_badge = f"{'🎗' if user.statistics['collectors_badge'] else ''}"

    all_cards_rolled = all(code in set(user.collection) for code, __ in roll_cards_dict.items())

    collectors_badge_redeem_s = ("\n\n<i>Вам доступна возможность получить Ленту Коллекционера. Для ознакомления "
                                 "нажмите /collectors_ribbon_info</i>") if all_cards_rolled else ""

    banned_badge = "⚱️" if user.status == "banned" else ""
    days_in_game = int((datetime.datetime.now().timestamp() - user.date_of_registration) // 86400) + 1

    packs_opened = user.statistics["packs_opened"]
    coins_spent = user.statistics["coins_spent"]
    trades_complete = user.statistics["trades_complete"]
    collectors_badges = user.statistics["collectors_badge"]

    response = (f"{banned_badge}<b>{user.username} • {user.id}</b>{collectors_badge}\n\n"
                f"🃏 Карт в коллекции: {cards_n}\n"
                f"💎 Уникальных: {unique_cards_n}\n"
                f"🪙 Монет: {user.coins}\n"
                f"📅 Дней в игре: <i>{days_in_game}</i>\n\n"
                f"🤝🏻 Обменов совершено: {trades_complete}\n"
                f"💸 Монет потрачено: {coins_spent}\n"
                f"⭐️ Достижения: /achievements"
                f"{collectors_badge_redeem_s}")

    await mes.reply_text(response,
                         reply_markup=main_menu_markup,
                         parse_mode="HTML")


async def achievements(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    await bot_check_achievements(update, _)

    if not user.achievements:
        await update.message.reply_text("У вас пока нет достижений. Играйте больше, чтобы их получить!")
        return

    resp = "<i><b>Ваши достижения:</b></i>\n\n"

    for ach in user.achievements:
        ach = achievements_dict[ach]
        resp += f"<b>{ach['name']}</b> — <i>{ach['desc']}</i>\n"

    await update.message.reply_text(resp,
                                    parse_mode="HTML")
