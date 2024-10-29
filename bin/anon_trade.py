import math
from typing import Literal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.init import USER_COLLECTION
from lib.keyboard_markup import CARDS_PER_PAGE, trades_menu_markup
from lib.variables import cards_dict


def get_active_offers_list(user_id):
    offers_raw = USER_COLLECTION.find({}, {"id": 1, "anon_trade": 1, "_id": 0})
    offers = set()

    for user in offers_raw:
        if 'anon_trade' in user:
            if user_id != user['id']:
                offers.update(offer['wts'] for offer in user['anon_trade'])

    result = {card_code: cards_dict[card_code] for card_code in offers}
    return result


def generate_trade_offers_keyboard(context, **kwargs):
    offers = list(kwargs["offers"])
    page = kwargs.get('page', 0)
    total_pages = math.ceil(len(offers) / CARDS_PER_PAGE)
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_offers = offers[start:end]

    keyboard = []
    is_my_offers = kwargs.get('type') == 'my_offers'
    collection = []
    if not is_my_offers:
        collection = list(set(User.get(None, kwargs['user_id']).collection))

    for offer in current_page_offers:
        if is_my_offers:
            context.user_data["anon_trade_my_offers"] = offers
            wts, wtb = offer['wts'], offer['wtb']
            if any([x not in cards_dict for x in [wts, wtb]]):
                continue
            wts_name, wtb_name = cards_dict[wts]['name'], cards_dict[wtb]['name']
            keyboard.append([InlineKeyboardButton(f"{wtb_name} за вашу {wts_name}",
                                                  callback_data=f"anon_trade_my_offer_{wts}_{wtb}")])
        else:
            offer_terms = list(offer.values())[0]
            if offer_terms['wts'] not in cards_dict or offer_terms['wtb'] not in cards_dict:
                continue
            offer_user = list(offer.keys())[0]
            card_name = cards_dict[offer_terms['wtb']]['name']
            card_code = offer_terms['wtb']
            keyboard.append([InlineKeyboardButton(f"Обмен на {card_name}"
                                                  f"{' ✖️' if card_code not in collection else ''}",
                                                  callback_data=f"anon_trade_view_offer_{offer_user}_"
                                                  f"{offer_terms['wts']}_{offer_terms['wtb']}")])

    # Кнопки навигации
    nav_buttons = []
    base_callback = "anon_trade_view_my_offers_page_" if is_my_offers else "anon_trade_view_offer_page_"

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("<<", callback_data=f"{base_callback}0"))
        nav_buttons.append(InlineKeyboardButton("<", callback_data=f"{base_callback}{page - 1}"))
    if len(offers) > CARDS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton(f"{page + 1}",
                                                callback_data="noop"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"{base_callback}{page + 1}"))
        nav_buttons.append(InlineKeyboardButton(">>", callback_data=f"{base_callback}{total_pages - 1}"))

    if not current_page_offers:
        keyboard.append([InlineKeyboardButton("Предложения отсутствуют", callback_data="noop")])
    else:
        if nav_buttons:
            keyboard.append(nav_buttons)

    # Кнопка "Назад"
    back_callback = "anon_trade_my_offers_close" if is_my_offers else "anon_trade_view_buy_list"
    back_text = "Закрыть" if is_my_offers else "Назад"
    keyboard.append([InlineKeyboardButton(back_text, callback_data=back_callback)])

    return InlineKeyboardMarkup(keyboard)


def generate_trade_keyboard(context, mode: Literal["buy", "sell"], **kwargs):
    active_offers = get_active_offers_list(kwargs['user_id']) if mode == "buy" else cards_dict
    page = int(kwargs["page"])
    context.user_data['anon_trade_page'] = page

    total_pages = math.ceil(len(active_offers) / CARDS_PER_PAGE)

    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    cards_list = list(set(card['code'] for card in list(active_offers.values())))
    cards_list.sort()
    current_page_cards = cards_list[start:end]
    wts = f"_{kwargs.get('wts')}" if 'wts' in kwargs else ""
    wtb = f"_{kwargs.get('wtb')}" if 'wtb' in kwargs else ""

    keyboard = []
    for card_code in current_page_cards:
        card = next(card for card in list(active_offers.values()) if card['code'] == card_code)
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

    if len(active_offers) > CARDS_PER_PAGE:
        nav_buttons.append(InlineKeyboardButton(f"{page + 1}",
                                                callback_data="noop"))

    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(">", callback_data=f"anon_trade_{mode}_page_{page + 1}{wts}{wtb}"))
        nav_buttons.append(InlineKeyboardButton(">>",
                                                callback_data=f"anon_trade_{mode}_page_{total_pages - 1}{wts}{wtb}"))

    if not current_page_cards:
        keyboard.append([InlineKeyboardButton("Предложения отсутствуют", callback_data="noop")])
    else:
        if nav_buttons:
            keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("Закрыть",
                                          callback_data=f"anon_trade_close_{mode}{wts}{wtb}")])

    return InlineKeyboardMarkup(keyboard)


async def anon_trade_main_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    await mes.reply_text("🗂",
                         reply_markup=trades_menu_markup)


async def anon_trade_choose_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    reply_markup = generate_trade_keyboard(context, mode="buy",
                                           page=kwargs['page'] if 'page' in kwargs else 0,
                                           user_id=user_id)
    resp = "Доступные предложения обмена:"
    if update.callback_query:
        # await update.callback_query.delete_message()
        await update.callback_query.edit_message_text(resp,
                                                      reply_markup=reply_markup)
        return
    await update.effective_chat.send_message(resp,
                                             reply_markup=reply_markup)


async def anon_trade_select_desired(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    reply_markup = generate_trade_keyboard(context, mode="sell", wts=kwargs['wts'], page=kwargs['page'],
                                           user_id=update.callback_query.from_user.id)
    resp = "Выберите желаемую карту"
    await context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                                   text=resp,
                                   reply_markup=reply_markup)


async def anon_trade_confirm_sell(update: Update, _: ContextTypes.DEFAULT_TYPE, **kwargs):
    wts = kwargs['wts']
    wtb = kwargs['wtb']
    wts_name = cards_dict[wts]['name']
    wtb_name = cards_dict[wtb]['name']
    resp = ("Вы уверены, что хотите создать предложение обмена?\n\n"
            f"Отдаёте: {wts_name}\n"
            f"Получаете: {wtb_name}")

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Да",
                                                               callback_data=f"anon_trade_confirm_sell_{wts}_{wtb}")],
                                         [InlineKeyboardButton("Отмена",
                                                               callback_data=f"anon_trade_cancel_sell_{wts}")]])

    await update.callback_query.edit_message_text(text=resp,
                                                  reply_markup=reply_markup)


async def anon_trade_buy_card_show_offers(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    await update.callback_query.answer()
    card_code = kwargs["card_code"]
    users = USER_COLLECTION.find({"status": {"$ne": "banned"}}, {"_id": 0})
    users = [{x["id"]: x["anon_trade"]} for x in users]
    offers = []
    for user in users:
        for uid, offers_list in user.items():
            for offer in offers_list:
                for mode, code in offer.items():
                    if (code == card_code and mode == 'wts') and uid != update.callback_query.from_user.id:
                        offers.append({uid: {"wts": offer.get("wts"), "wtb": offer.get("wtb")}})

    try:
        _ = context.user_data["anon_trade_page"]
    except KeyError:
        context.user_data["anon_trade_page"] = 0

    context.user_data["anon_trade_offers"] = offers

    card_name = cards_dict[card_code]['name']
    response = f"Предложения по {card_name}:"
    keyboard = generate_trade_offers_keyboard(context, offers=offers, user_id=update.callback_query.from_user.id)

    await update.callback_query.edit_message_text(response, reply_markup=keyboard)


async def anon_trade_show_my_offers(update: Update, context: ContextTypes.DEFAULT_TYPE, **kwargs):
    page = kwargs.get('page', 0)
    if not update.callback_query:
        user = User.get(update.message.from_user)
    else:
        user = User.get(update.callback_query.from_user)
    keyboard = generate_trade_offers_keyboard(context, offers=user.anon_trade, type='my_offers', page=page)
    if not update.callback_query:
        await update.message.reply_text("Ваши предложения обмена:", reply_markup=keyboard)
        return
    await update.callback_query.edit_message_text("Ваши предложения обмена:",
                                                  reply_markup=keyboard)


async def anon_trade_show_my_offer(update: Update, _: ContextTypes.DEFAULT_TYPE, **kwargs):
    wts, wtb = kwargs['wts'], kwargs['wtb']
    resp = ("Ваше предложение обмена:\n"
            f"Предлагаете: {cards_dict[wts]['name']}\n"
            f"В обмен на: {cards_dict[wtb]['name']}")
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отменить предложение",
                                                           callback_data="anon_trade_my_offer_"
                                                                         f"remove_{wts}_{wtb}")],
                                     [InlineKeyboardButton("Назад", callback_data="anon_trade_show_my_offers")]])
    await update.callback_query.edit_message_text(resp,
                                                  reply_markup=keyboard)
