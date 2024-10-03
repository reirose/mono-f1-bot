import math

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import CARDS_PER_PAGE
from lib.variables import cards_dict


def generate_trade_keyboard(context):
    page = context.user_data["page"]

    total_pages = math.ceil(len(cards_dict) / CARDS_PER_PAGE)

    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    cards_list = list(set(card['code'] for card in list(cards_dict.values())))
    cards_list.sort()
    current_page_cards = cards_list[start:end]

    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in list(cards_dict.values()) if card['code'] == card_code)
        button_text = f"{card['name']}"
        keyboard.append([InlineKeyboardButton(button_text,
                                              callback_data=f"anon_trade_{card['code']}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<", callback_data=f"page_0"))
        nav_buttons.append(InlineKeyboardButton("<",
                                                callback_data=f"anon_trade_page_{page - 1}"))
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}", callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"anon_trade_page_{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(">>",
                                                callback_data=f"anon_trade_page_{total_pages - 1}"))

    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("Закрыть", callback_data="anon_trade_close")])

    return InlineKeyboardMarkup(keyboard)


async def anon_trade_choose_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # user = User.get(update.effective_user)
    context.user_data["page"] = 0
    reply_markup = generate_trade_keyboard(context)
    resp = "Выберите карту, по которой хотите посмотреть предложения"
    await update.message.reply_text(resp,
                                    reply_markup=reply_markup)


async def anon_trade_show_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
