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


async def generate_collection_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                       telegram_user_id, page: int, in_market: bool, trade=None,
                                       trade_receiver: int = None):
    """
    Генерация списка карт в просмотре коллекции ( взято с чатгпт, поэтому трогать не советую с: )
    :param trade_receiver: ~~
    :param trade: ~~
    :param context: ~~
    :param update: ~~
    :param in_market: для маркета
    :param telegram_user_id: id юзера
    :param page: текущая страница
    :return: маркап текущей страницы клавиатуры
    """
    user_cards = User.get(user=None, update=telegram_user_id).collection
    user_cards = [cards_dict[x] for x in user_cards]
    user_trade = User.get(user=None, update=telegram_user_id).trade

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
    market = "market_" if in_market else ''
    trade_s = "trade_" if trade else ''

    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in user_cards if card['code'] == card_code)
        count = card_counter[card_code]
        button_text = f"{card['name']} {f'(x{count})'} {'✅' if card_code in user_trade else ''}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{market}{trade_s}{card['code']}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<", callback_data=f"{trade_s}{market}page_0"))
        nav_buttons.append(InlineKeyboardButton("<", callback_data=f"{trade_s}{market}page_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"{trade_s}{market}page_{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(">>", callback_data=f"{trade_s}{market}page_{total_pages - 1}"))

    keyboard.append(nav_buttons)
    if trade:
        keyboard += [[InlineKeyboardButton('Подтвердить',
                                           callback_data=f'trade_confirm'
                                                         f'_{trade_receiver}')],
                     [InlineKeyboardButton('Отмена', callback_data="trade_cancel")]]

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


main_menu_buttons = [KeyboardButton("Получение карт"), KeyboardButton("Коллекция"),
                     KeyboardButton("Обо мне"), KeyboardButton("Другое")]

roll_menu_buttons = [[KeyboardButton("Открыть пак")], [KeyboardButton("Магазин"), KeyboardButton("Меню")]]

shop_menu_buttons = [[KeyboardButton("Паки"), KeyboardButton("Получение карт")],
                     [KeyboardButton("Меню")]]

other_menu_buttons = [[KeyboardButton("Монетка"),  # KeyboardButton("Битва картами")],
                      KeyboardButton("Все карты")], [KeyboardButton("MonoF1"), KeyboardButton("Меню")]]

coinflip_menu_buttons = [[KeyboardButton("С игроком"), KeyboardButton("С ботом")], [KeyboardButton("Меню")]]

collection_menu_buttons = [KeyboardButton("Список карт"), KeyboardButton("Посмотреть карту"),
                           KeyboardButton("Отправить"), KeyboardButton("Трейды"),
                           KeyboardButton("Меню")]

trades_menu_buttons = [[KeyboardButton("Предложения игроков"), KeyboardButton("Мои предложения")],
                       [KeyboardButton("Коллекция"), KeyboardButton("Меню")]]

trades_menu_markup = ReplyKeyboardMarkup(trades_menu_buttons, resize_keyboard=True)
main_menu_markup = ReplyKeyboardMarkup(build_menu(main_menu_buttons, n_cols=2), resize_keyboard=True)
roll_menu_markup = ReplyKeyboardMarkup(roll_menu_buttons, resize_keyboard=True)
other_menu_markup = ReplyKeyboardMarkup(other_menu_buttons, resize_keyboard=True)
shop_menu_markup = ReplyKeyboardMarkup(shop_menu_buttons, resize_keyboard=True)
coinflip_menu_markup = ReplyKeyboardMarkup(coinflip_menu_buttons, resize_keyboard=True)
collection_menu_markup = ReplyKeyboardMarkup(build_menu(collection_menu_buttons, n_cols=3), resize_keyboard=True)
