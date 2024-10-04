import math
from typing import Literal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from lib.init import USER_COLLECTION
from lib.keyboard_markup import CARDS_PER_PAGE
from lib.variables import cards_dict


def generate_trade_keyboard(context, mode: Literal["buy", "sell"], **kwargs):
    page = context.user_data["page"]

    total_pages = math.ceil(len(cards_dict) / CARDS_PER_PAGE)

    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    cards_list = list(set(card['code'] for card in list(cards_dict.values())))
    cards_list.sort()
    current_page_cards = cards_list[start:end]
    wts = f"_{kwargs.get('wts')}" if 'wts' in kwargs else ""
    wtb = f"_{kwargs.get('wtb')}" if 'wtb' in kwargs else ""

    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in list(cards_dict.values()) if card['code'] == card_code)
        button_text = f"{card['name']}"
        card_code = card_code if not any([wtb, wtb]) else ""
        keyboard.append([InlineKeyboardButton(button_text,
                                              callback_data=f"anon_trade_{mode}_{card_code}{wts}{wtb}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<",
                                                callback_data=f"anon_trade_{mode}_page_0{wts}{wtb}"))
        nav_buttons.append(InlineKeyboardButton("<",
                                                callback_data=f"anon_trade_{mode}_page_{page - 1}{wts}{wtb}"))
    nav_buttons.append(InlineKeyboardButton(f"{page + 1}",
                                            callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"anon_trade_{mode}_page_{page + 1}{wts}{wtb}"))
        nav_buttons.append(InlineKeyboardButton(">>",
                                                callback_data=f"anon_trade_{mode}_page_{total_pages - 1}{wts}{wtb}"))

    keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("Закрыть",
                                          callback_data=f"anon_trade_close_{mode}{wts}{wtb}")])

    return InlineKeyboardMarkup(keyboard)


async def anon_trade_choose_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["page"] = 0
    reply_markup = generate_trade_keyboard(context, mode="buy")
    resp = "Выберите карту, по которой хотите посмотреть предложения"
    await update.callback_query.delete_message()
    await update.effective_chat.send_message(resp,
                                             reply_markup=reply_markup)


async def anon_trade_select_desired(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["page"] = 0
    reply_markup = generate_trade_keyboard(context, mode="sell", wts=context.user_data["wts"])
    resp = "Выберите желаемую карту"
    await context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                   text=resp,
                                   reply_markup=reply_markup)


async def anon_trade_confirm_sell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wts = context.user_data['wts']
    wtb = context.user_data['wtb']
    resp = ("Вы уверены, что хотите создать предложение обмена?\n\n"
            f"Отдаёте: {wts}\n"
            f"Получаете: {wtb}")

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Да",
                                                               callback_data=f"anon_trade_confirm_sell_{wts}_{wtb}")],
                                         [InlineKeyboardButton("Отмена",
                                                               callback_data="anon_trade_cancel_sell")]])

    await update.callback_query.edit_message_text(text=resp,
                                                  reply_markup=reply_markup)


async def anon_trade_buy_card_show_offers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    card_code = context.user_data["card_code"]
    users = USER_COLLECTION.find({"status": {"$ne": "banned"}}, {"_id": 0})
    users = [{x["id"]: x["anon_trade"]} for x in users]
    offers = []
    for user in users:
        for uid, offers_list in user.items():
            for offer in offers_list:
                for mode, code in offer.items():
                    if code == card_code:
                        offers.append({uid: {"wts": offer.get("wts"), "wtb": offer.get("wtb")}})

    response = f"Предложения по {card_code}:"
    keyboard = []
    for offer in offers:
        offer_terms = list(offer.values())[0]
        offer_user = list(offer.keys())[0]
        keyboard.append([InlineKeyboardButton(f"Обмен на {offer_terms['wts']}",
                                              callback_data=f"anon_trade_view_offer_{offer_user}_"
                                                            f"{offer_terms['wts']}_{offer_terms['wtb']}")])
    if not keyboard:
        keyboard.append([InlineKeyboardButton("Предложения отсутствуют", callback_data="noop")])
    keyboard.append([InlineKeyboardButton("Назад", callback_data="anon_trade_view_buy_list")])

    await update.callback_query.edit_message_text(response, reply_markup=InlineKeyboardMarkup(keyboard))
