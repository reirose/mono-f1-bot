import datetime
import random
import re

from typing import Literal

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from bin.achievements import bot_check_achievements
from bin.collection import get_card_image
from lib.classes.user import User
from lib.init import BOT_INFO, logger
from lib.keyboard_markup import roll_menu_markup
from lib.variables import cards_by_category, translation, garant_list, \
    roll_cards_dict, category_sort_keys, garant_value, category_distribution, cards_dict, \
    cumulative_probability_by_category, MAX_CARDS_IN_PACK


def generate_available_packs_keyboard(user: User):
    keyboard = []
    for pack_type, count in user.rolls_available.items():
        if not count:
            continue
        if pack_type == "gold":
            pack_type = "pack_gold"
        keyboard.append([InlineKeyboardButton(f"{translation[pack_type]} - {count} шт.",
                                              callback_data=f"pack_open_{pack_type}")])
    if not keyboard:
        keyboard.append([InlineKeyboardButton("Пустовато тут у вас с:",
                                              callback_data="noop")])
    return InlineKeyboardMarkup(keyboard)


async def packs_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("Доступные паки:",
                                             reply_markup=generate_available_packs_keyboard(
                                                 User.get(update.effective_user)))


def get_pack_variables(pack_type: Literal["standard", "pack_gold", "gem"]) -> (dict, dict, int):
    return category_distribution[pack_type], cumulative_probability_by_category[pack_type], MAX_CARDS_IN_PACK[pack_type]


def select_card_weighted(garant: bool = None, user: User = None,
                         pack_type: Literal["standard", "pack_gold", "gem"] = "standard") -> list[dict]:
    pack_category_distribution, \
        pack_cumulative_probability_by_category, \
        pack_MAX_CARDS_IN_PACK = get_pack_variables(pack_type=pack_type)
    categories = []
    for category, count in pack_category_distribution.items():
        for _ in range(count):
            categories.append(category)

    rand = random.random()
    for category, prob in pack_cumulative_probability_by_category.items():
        if len(categories) > pack_MAX_CARDS_IN_PACK:
            break
        if rand < prob:
            categories.append(category)
            break

    if not any(cat in ["gold", "ruby", 'sapphire', 'platinum'] for cat in categories) and garant:
        logger.log(BOT_INFO, "garant rolled")
        categories.append(random.choices(["gold", "platinum", "ruby", "sapphire"],
                                         [.5460, .2009, .0739, .0272])[0])

    rolled_cards = []
    for cat in categories:
        try:
            card = roll_cards_dict[random.choice(cards_by_category[cat])]
        except IndexError:
            continue
        while card in rolled_cards or card["code"] in user.last_roll:
            card = roll_cards_dict[random.choice(cards_by_category[cat])]
        rolled_cards.append(card)

    user.last_roll = [x["code"] for x in rolled_cards]
    user.write()
    return rolled_cards


async def roll_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    now = datetime.datetime.now()
    nextday = True if (now.hour > 8 and now.hour >= 20) or (now.hour < 8) else False
    next_free_roll_time = datetime.datetime(hour=8 if nextday else 20,
                                            minute=0,
                                            second=0,
                                            year=now.year,
                                            month=now.month,
                                            day=now.day) - now
    hrs = int(next_free_roll_time.seconds // 3600)
    mins = int((next_free_roll_time.seconds % 3600) // 60)
    time_left = "меньше минуты" if (not hrs and not mins and not (next_free_roll_time // 60)) \
        else f"{hrs} ч {mins} мин"

    response = (f"🃏 <b>Доступно паков:</b> {sum(user.rolls_available.values())}\n"
                f"Гарант: {user.garant}\n\n"
                f"До следующего бесплатного пака: {time_left}")

    await mes.reply_text(response,
                         parse_mode="HTML",
                         reply_markup=roll_menu_markup)


# noinspection PyTypeChecker
async def roll_new(update: Update, _: ContextTypes.DEFAULT_TYPE, **kwargs):
    pack_type = kwargs.get("pack_type", "standard")
    user = User.get(update.effective_user)

    if user.status == 'rolling':
        await update.effective_chat.send_message(text="Вы уже открываете пак!")
        return

    if not user.rolls_available or user.rolls_available.get(pack_type) <= 0:
        now = datetime.datetime.now()
        next_free_roll_time = datetime.datetime(
            hour=8 if now.hour < 8 or now.hour >= 20 else 20,
            minute=0,
            second=0,
            year=now.year,
            month=now.month,
            day=now.day
        ) - now

        hrs, remainder = divmod(next_free_roll_time.seconds, 3600)
        mins, _ = divmod(remainder, 60)
        time_left = "меньше минуты" if next_free_roll_time.seconds < 60 else f"{hrs} ч {mins} мин"

        await update.effective_chat.send_message(f"У вас не осталось паков!\n\nДо получения бесплатного: "
                                                 f"{time_left}")
        return

    garant = user.garant >= garant_value
    rolled_cards = sorted(select_card_weighted(garant=garant, user=user, pack_type=pack_type),
                          key=lambda x: category_sort_keys.get(x['category'], float('inf')))

    logger.log(BOT_INFO, f"{user.username} rolled: {', '.join([card['name'] for card in rolled_cards])}")

    card = rolled_cards[0]
    rolled_cards.pop(0)

    user.garant = 0 if (garant or any(
        card in garant_list for card in [x["category"] for x in rolled_cards])) else user.garant + 1
    user.status = 'rolling'
    user.statistics["packs_opened"] += 1
    user.rolls_available[pack_type] -= 1
    callback_data = "roll" + "".join([f"_{x['code']}" for x in rolled_cards])
    cards_left_s = f" ({len(rolled_cards)})"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"Следующая карта{cards_left_s}", callback_data=callback_data)]])

    try:
        card_pic = get_card_image(card['code'])
    except FileNotFoundError:
        card_pic = open("bin/img/card.png", 'rb')

    await update.effective_chat.send_photo(
        card_pic,
        caption=f"Получена карта: {translation.get(card['category'])} {card['name']}!"
                f"{' 🆕' if card['code'] not in user.collection else ''}",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    user.collection.append(card['code'])
    user.write()


async def roll_new_continue(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    await update.callback_query.edit_message_reply_markup(reply_markup=None)

    cards = [cards_dict.get(x) for x in re.findall(r"(c_\d{3})", update.callback_query.data)]
    card = cards[0]
    cards.pop(0)

    if cards:
        cards_left_s = f" ({len(cards)})"
        callback_data = "roll" + "".join([f"_{x['code']}" for x in cards])
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(f"Следующая карта{cards_left_s}", callback_data=callback_data)]])
    else:
        keyboard = []
        for pack_type, count in user.rolls_available.items():
            if count:
                keyboard.append([InlineKeyboardButton(f"Открыть {translation[pack_type]} пак",
                                                      callback_data=f"pack_open_{pack_type}")])
        user.status = "idle"
        keyboard = InlineKeyboardMarkup(keyboard) if keyboard else None

    try:
        card_pic = get_card_image(card['code'])
    except FileNotFoundError:
        card_pic = open("bin/img/card.png", 'rb')

    await update.effective_user.send_photo(
        card_pic,
        caption=f"Получена карта: {translation.get(card['category'])} {card['name']}!"
                f"{' 🆕' if card['code'] not in user.collection else ''}",
        parse_mode="HTML",
        reply_markup=keyboard
    )

    user.collection.append(card['code'])
    user.write()

    await bot_check_achievements(update, _)
