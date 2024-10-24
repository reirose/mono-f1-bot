import math
import re
import uuid

import pymongo
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, \
    CommandHandler

from bin.collection import collection_menu, send_card_list
from lib.classes.user import User
from lib.init import MARKET_COLLECTION
from lib.keyboard_markup import shop_menu_markup, CARDS_PER_PAGE
from lib.variables import cards_dict


async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text="🛒",
                                   chat_id=update.callback_query.from_user.id if update.callback_query
                                   else update.message.from_user.id,
                                   reply_markup=shop_menu_markup)


def generate_market_my_offers_keyboard(**kwargs):
    user = kwargs.get("user", None)
    page = kwargs.get("page", 0)
    if not user:
        return None

    offers = list(MARKET_COLLECTION.find({"seller": user.id}))
    page = kwargs.get('page', 0)
    total_pages = math.ceil(len(offers) / CARDS_PER_PAGE)
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_offers = offers[start:end]
    keyboard = []
    for offer in current_page_offers:
        if offer['code'] not in cards_dict:
            continue
        callback = "market_my_offer_show_"
        card_name = cards_dict[offer["code"]]['name']
        price = offer['price']
        keyboard.append([InlineKeyboardButton(f"{card_name} - {price}",
                                              callback_data=f"{callback}{offer['id']}")])

    # Кнопки навигации
    nav_buttons = []
    base_callback = "market_my_offers_page_"

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
    back_callback = "market_offers_close"
    back_text = "Закрыть"
    keyboard.append([InlineKeyboardButton(back_text, callback_data=back_callback)])

    return InlineKeyboardMarkup(keyboard)


def generate_market_card_offers_keyboard(**kwargs):
    user = kwargs.get("user", None)
    card_code = kwargs.get("card_code", None)
    if not any([user, card_code]):
        return
    offers = list(MARKET_COLLECTION.find({"code": card_code,
                                          "seller": {"$ne": user.username}}, {"_id": 0}).sort("price",
                                                                                              pymongo.ASCENDING))

    page = kwargs.get('page', 0)
    total_pages = math.ceil(len(offers) / CARDS_PER_PAGE)
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_offers = offers[start:end]
    keyboard = []
    for offer in current_page_offers:
        if offer['code'] not in cards_dict:
            continue
        callback = "market_offer_show_"
        card_name = cards_dict[offer["code"]]['name']
        price = offer['price']
        keyboard.append([InlineKeyboardButton(f"{card_name} - {price}",
                                              callback_data=f"{callback}{offer['id']}")])

    # Кнопки навигации
    nav_buttons = []
    base_callback = "market_offer_card_page_"

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
    back_callback = "market_offers"
    back_text = "Назад"
    keyboard.append([InlineKeyboardButton(back_text, callback_data=back_callback)])

    return InlineKeyboardMarkup(keyboard)


def generate_market_offers_keyboard(_, **kwargs):
    user = kwargs.get("user", None)
    if not user:
        return
    offers_raw = list(MARKET_COLLECTION.find({"seller": {"$ne": user.id}}))
    offers = sorted(list(set([x['code'] for x in offers_raw])), key=lambda x: int(x.split('_')[1]))
    page = kwargs.get('page', 0)
    total_pages = math.ceil(len(offers) / CARDS_PER_PAGE)
    start = page * CARDS_PER_PAGE
    end = start + CARDS_PER_PAGE
    current_page_offers = offers[start:end]

    keyboard = []
    is_my_offers = kwargs.get('type') == 'my_offers'

    for offer in current_page_offers:
        if is_my_offers:
            pass
        else:
            if offer not in cards_dict:
                continue
            callback = "market_offer_card_"
            card_name = cards_dict[offer]['name']
            keyboard.append([InlineKeyboardButton(f"{card_name}",
                                                  callback_data=f"{callback}{offer}")])

    # Кнопки навигации
    nav_buttons = []
    base_callback = "market_offers_page_"

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
    back_callback = "market_offers_close"
    back_text = "Закрыть"
    keyboard.append([InlineKeyboardButton(back_text, callback_data=back_callback)])

    return InlineKeyboardMarkup(keyboard)


async def market_menu_new(update: Update, _: ContextTypes.DEFAULT_TYPE):
    keyboard = ReplyKeyboardMarkup([[KeyboardButton("Предложения игрокoв"), KeyboardButton("Мoи предложения")],
                                    [KeyboardButton("Меню")]], resize_keyboard=True)
    await update.effective_chat.send_message("💸",
                                             reply_markup=keyboard)


async def market_offers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = generate_market_offers_keyboard(context, user=User.get(update.effective_user))
    if update.callback_query:
        try:
            page = int(update.callback_query.data.split("_")[-1])
        except ValueError:
            page = 0
        keyboard = generate_market_offers_keyboard(context, user=User.get(update.effective_user), page=page)
        await update.callback_query.edit_message_text("Выберите карту, по которой хотите посмотреть предложения:",
                                                      reply_markup=keyboard)
        return
    await update.effective_chat.send_message("Выберите карту, по которой хотите посмотреть предложения:",
                                             reply_markup=keyboard)


async def market_offers_show_card(update: Update, _: ContextTypes.DEFAULT_TYPE):
    card_code = re.search("market_offer_card_(.+)", update.callback_query.data).group(1)
    keyboard = generate_market_card_offers_keyboard(user=User.get(update.effective_user), card_code=card_code)
    card_name = cards_dict.get(card_code).get("name", None)
    await update.callback_query.edit_message_text(text=f"Предложения по карте {card_name}",
                                                  reply_markup=keyboard)


async def market_offer_show(update: Update, _: ContextTypes.DEFAULT_TYPE):
    offer_id = re.search("market_offer_show_(.+)", update.callback_query.data).group(1)
    offer = MARKET_COLLECTION.find_one({"id": offer_id})
    if not offer:
        await update.callback_query.answer("Ошибка: предложение больше не существует!")
        return

    card_name = cards_dict.get(offer["code"])["name"]
    seller = User.get(None, update=offer["seller"]).username
    price = offer["price"]
    resp = (f"Предложение по карте <b>{card_name}</b>:\n\n"
            f"Продавец: <i>{seller}</i>\n"
            f"Цена: <i>{price} 🪙</i>")
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"Купить за {price} 🪙",
                                                           callback_data=f"market_buy_offer_{offer_id}")],
                                     [InlineKeyboardButton("Назад",
                                                           callback_data=f"market_offer_card_{offer['code']}")]])
    await update.callback_query.edit_message_text(resp, reply_markup=keyboard, parse_mode="HTML")


async def market_buy_offer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buyer = User.get(update.effective_user)
    offer_id = re.search("market_buy_offer_(.+)", update.callback_query.data).group(1)
    offer = MARKET_COLLECTION.find_one({"id": offer_id})
    if not offer:
        print(1)
        await update.callback_query.answer("Ошибка: предложения больше не существует!", show_alert=True)
        return

    if int(offer.get("price")) > buyer.coins:
        await update.callback_query.answer("Тебе не хватит денег даже на кружку пива. Иди зарабатывать.",
                                           show_alert=True)
        return

    price = int(offer.get("price"))
    seller = User.get(None, update=offer['seller'])
    buyer.coins -= price
    buyer.collection.append(offer['code'])
    seller.coins += price
    buyer.write()
    seller.write()
    MARKET_COLLECTION.delete_one({"id": offer_id})
    await update.effective_chat.send_message(f"Получена карточка: <b>{cards_dict[offer['code']]['name']}</b>",
                                             parse_mode="HTML")
    await update.callback_query.delete_message()
    await context.bot.send_message(chat_id=seller.id,
                                   text=f"У вас купили карточку <b>{cards_dict[offer['code']]['name']}</b>"
                                        f" за {price} 🪙",
                                   parse_mode="HTML")


async def market_sell_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.delete_message()
    card_code = re.search("market_sell_card_(.+)", update.callback_query.data).group(1)
    context.user_data["market_sell_card_code"] = card_code
    if card_code not in User.get(update.effective_user).collection:
        return ConversationHandler.END
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data=card_code)]])
    sent = await update.effective_user.send_message("Введите цену, по которой хотите продать карту: ",
                                                    reply_markup=keyboard)
    context.user_data["price_input_message_id"] = sent.message_id
    return "market_sell_card_parse_price"


async def handle_market_sell_card_parse_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    card_code = context.user_data.get("market_sell_card_code", None)
    if not card_code:
        return ConversationHandler.END

    try:
        price = int(update.message.text)
    except ValueError:
        await update.effective_user.send_message("Неверный ввод.")
        return "market_sell_card_parse_price"

    await update.effective_chat.delete_message(context.user_data.get("price_input_message_id"))

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(f"Продать за {price} 🪙",
                                                           callback_data=f"market_confirm_sell_"
                                                                         f"card_{card_code}_{price}")],
                                     [InlineKeyboardButton("Отмена", callback_data=card_code)]])

    response = f"Вы уверены, что хотите продать карту <b>{cards_dict[card_code]['name']}</b> за <i>{price} 🪙</i>?"
    await update.effective_user.send_message(response,
                                             reply_markup=keyboard,
                                             parse_mode="HTML")
    return ConversationHandler.END


async def market_confirm_sell_card(update: Update, _: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    card_code = re.search(r"c_\d{3}", update.callback_query.data).group(0)
    price = int(update.callback_query.data.split("_")[-1])
    MARKET_COLLECTION.insert_one({"id": uuid.uuid4().hex[-8:],
                                  "code": card_code,
                                  "seller": user.id,
                                  "price": price})
    user.collection.remove(card_code)
    user.write()
    await update.callback_query.edit_message_text(f"Вы выставили карту {cards_dict[card_code]['name']}"
                                                  f" на Маркете за {price} 🪙",
                                                  reply_markup=None)
    await send_card_list(update, _, in_market=False, trade_receiver=False, telegram_user=update.effective_user, page=0)


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(market_sell_card, pattern=r'market_sell_card_c_\d{3}')],
    states={
        "market_sell_card_parse_price": [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                                        handle_market_sell_card_parse_price)],
    },
    fallbacks=[CommandHandler("cancel", collection_menu)]
)


async def market_show_my_offers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    page = 0
    if update.callback_query:
        try:
            page = int(update.callback_query.data.split("_")[-1])
        except ValueError:
            pass
    kb = generate_market_my_offers_keyboard(user=user, page=page)
    resp = "Список Ваших предложений:"
    if update.callback_query:
        await update.callback_query.edit_message_text(text=resp,
                                                      reply_markup=kb)
        return
    await update.effective_chat.send_message(text=resp,
                                             reply_markup=kb)


async def market_my_offer_show(update: Update, context: ContextTypes.DEFAULT_TYPE):
    offer_id = update.callback_query.data.split("_")[-1]
    offer = MARKET_COLLECTION.find_one({"id": offer_id})
    resp = ("Предложение по карточке:\n"
            f"Карта: <b>{cards_dict[offer['code']]['name']}</b>\n"
            f"Цена: <i>{offer['price']}</i> 🪙")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("Отменить", callback_data=f"market_offer_remove_{offer_id}")],
                               [InlineKeyboardButton("Назад", callback_data="market_my_offers_list")]])
    await update.callback_query.edit_message_text(resp,
                                                  reply_markup=kb,
                                                  parse_mode="HTML")


async def market_offer_remove(update: Update, _):
    offer_id = update.callback_query.data.split("_")[-1]
    offer = MARKET_COLLECTION.find_one({"id": offer_id})
    if not offer or offer['code'] not in cards_dict:
        await update.callback_query.answer()
        return

    user = User.get(update.effective_user)
    user.collection.append(offer['code'])
    user.write()
    MARKET_COLLECTION.delete_one({"id": offer_id})
    await market_show_my_offers_list(update, _)
