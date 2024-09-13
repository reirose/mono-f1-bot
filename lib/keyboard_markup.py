"""
Маркапы всех клавиатур в игре - тестовых и инлайн
"""


import math
from collections import Counter

from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.variables import cards_dict


CARDS_PER_PAGE = 7


async def generate_market_cards_keyboard(page):
    """
    Генерация списка карт в макрете ( взято с чатгпт, поэтому трогать не советую с: )
    :param page: текущая страница
    :return: маркап текущей страницы клавиатуры
    """
    cards = list(cards_dict.values())
    cards_codes_names = [{card["code"]: card["name"]} for card in cards]

    total_pages = math.ceil(len(cards_codes_names) / CARDS_PER_PAGE)
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_cards = list(cards_codes_names)[start:end]
    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in cards_codes_names if card['code'] == card_code)
        button_text = f"{card['name']}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"market_list_{card['code']}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<", callback_data=f"market_list_page_0"))
        nav_buttons.append(InlineKeyboardButton("<", callback_data=f"market_list_page_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"market_list_page_{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(">>", callback_data=f"market_list_page_{total_pages - 1}"))

    keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


async def generate_collection_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       telegram_user, page: int, in_market: bool):
    """
    Генерация списка карт в просмотре коллекции ( взято с чатгпт, поэтому трогать не советую с: )
    :param in_market: для маркета
    :param telegram_user: объект юзера
    :param page: текущая страница
    :return: маркап текущей страницы клавиатуры
    """
    user_cards = User.get(telegram_user).collection
    user_cards = [cards_dict[x] for x in user_cards]

    card_counter = Counter(card['code'] for card in user_cards)

    unique_cards = list(set(card['code'] for card in user_cards))
    unique_cards.sort()

    total_pages = math.ceil(len(unique_cards) / CARDS_PER_PAGE)

    if not unique_cards:
        await context.bot.send_message(text="У вас нет карточек. Чтобы получить их "
                                            "- перейдите в раздел Получение карт.",
                                       chat_id=update.effective_user.id,
                                       reply_markup=collection_menu_markup)
        return

    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_cards = unique_cards[start:end]
    market = "market_" if not in_market else ''

    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in user_cards if card['code'] == card_code)
        count = card_counter[card_code]
        button_text = f"{card['name']} {f'(x{count})'}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{market}{card['code']}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<", callback_data=f"{market}page_0"))
        nav_buttons.append(InlineKeyboardButton("<", callback_data=f"{market}page_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"{market}page_{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(">>", callback_data=f"{market}page_{total_pages - 1}"))

    keyboard.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(keyboard)
    return reply_markup


shop_inline_markup = InlineKeyboardMarkup([[InlineKeyboardButton("1 пак - 10 🪙", callback_data="pack_buy_1")],
                                           [InlineKeyboardButton("2 пака - 20 🪙", callback_data="pack_buy_2")],
                                           [InlineKeyboardButton("3 пака - 28 🪙", callback_data="pack_buy_3")],
                                           [InlineKeyboardButton("5 паков - 47 🪙", callback_data="pack_buy_5")],
                                           [InlineKeyboardButton("10 паков - 90 🪙", callback_data="pack_buy_10")]])


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None) -> list:
    """
    Функция для построениы текстовой клавиатуры
    :param buttons: список кнопок вида KeyboardButton("string")
    :param n_cols: количество столбцов в клавиатуре
    :param header_buttons: кнопки первого ряда (опционально)
    :param footer_buttons: кнопки последнего ряда (опционально)
    :return: список клавиатуры для бота
    """
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def get_collection_list(user_collection: list) -> list:
    return [KeyboardButton(x) for x in user_collection] + [KeyboardButton("Меню")] if user_collection \
        else [KeyboardButton("Меню")]


main_menu_buttons = [KeyboardButton("🏳️‍🌈 Получение карт"), KeyboardButton("🏳️‍🌈 Коллекция"),
                     KeyboardButton("🏳️‍🌈 Обо мне"), KeyboardButton("🏳️‍🌈 Другое")]

roll_menu_buttons = [KeyboardButton("🏳️‍🌈 Получить карту"), KeyboardButton("🏳️‍🌈 Меню")]

other_menu_buttons = [KeyboardButton("🏳️‍🌈 Магазин"), KeyboardButton("🏳️‍🌈 Маркет"),
                      KeyboardButton("🏳️‍🌈 MonoF1"), KeyboardButton("🏳️‍🌈 Меню")]

collection_menu_buttons = [KeyboardButton("🏳️‍🌈 Список карт"), KeyboardButton("🏳️‍🌈 Посмотреть карту"),
                           KeyboardButton("🏳️‍🌈 Меню")]

main_menu_markup = ReplyKeyboardMarkup(build_menu(main_menu_buttons, n_cols=2), resize_keyboard=True)
roll_menu_markup = ReplyKeyboardMarkup(build_menu(roll_menu_buttons, n_cols=2), resize_keyboard=True)
other_menu_markup = ReplyKeyboardMarkup(build_menu(other_menu_buttons, n_cols=2), resize_keyboard=True)
collection_menu_markup = ReplyKeyboardMarkup(build_menu(collection_menu_buttons, n_cols=2), resize_keyboard=True)
