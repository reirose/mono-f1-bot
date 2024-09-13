import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import collection_menu_markup, generate_collection_keyboard
from lib.variables import cards_dict, category_to_plain_text, type_to_plain_text, color_by_category


async def show_card(query, context, in_market: bool):
    user_collection = User.get(query.from_user).collection
    card = cards_dict.get(f"c_{re.search('c_(.{3})', query.data).group(1)}")
    card_pic_id = ("AgACAgQAAxkBAAIMP2bKLDHHQSdb4-"
                   "4qJpG9WTW7k8QtAAK0wTEbmxtZUuGYL8YF6ayLAQADAgADeAADNQQ")  # TODO: сделать оформление из файла
    card_name = card["name"]
    card_team = card["team"]
    card_category = category_to_plain_text[card["category"]]
    card_type = type_to_plain_text[card["type"]]
    card_n = user_collection.count(card["code"])
    response = (f"{card_name}\n\n"
                f"Команда: {card_team}\n"
                f"Тип карты: {card_type}\n"
                f"Редкость: {color_by_category[card['category']]} {card_category}\n\n"
                f"{f'<i>Всего: {card_n} шт.</i>' if card_n > 1 else ''}")

    market_s = "market_" if in_market else ""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Продать",
                                                               callback_data=market_s + "sell_" + card["code"])],
                                         [InlineKeyboardButton("Закрыть", callback_data=market_s + "close_card")]])

    await context.bot.send_photo(chat_id=query.message.chat.id,
                                 photo=card_pic_id,
                                 caption=response,
                                 parse_mode="HTML",
                                 reply_markup=reply_markup)
    try:
        await context.bot.delete_message(chat_id=query.from_user.id,
                                         message_id=query.message.message_id)
    except BadRequest:
        pass
    await query.answer()  # f"Вы выбрали карту {query.data}"


async def list_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    page = 0
    await send_card_list(update, context, user, page, True)


async def send_card_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         telegram_user, page: int, unique_only: bool) -> None:
    if not User.get(telegram_user).collection:
        await context.bot.send_message(text="У вас нет карточек. Чтобы получить их - "
                                            "перейдите в раздел Получение карт.",
                                       reply_markup=collection_menu_markup,
                                       chat_id=telegram_user.id)
        return
    reply_markup = await generate_collection_keyboard(update, context, telegram_user, page, unique_only)

    if update.callback_query and (not update.callback_query.data.startswith("sell_confirm_") and
                                  not update.callback_query.data == "close_card" and
                                  not update.callback_query.data.startswith("market_close_")):
        await update.callback_query.answer()
        await update.callback_query.edit_message_text("Ваш список карт:", reply_markup=reply_markup)
        return
    else:
        await context.bot.send_message(text="Ваш список карт:",
                                       chat_id=telegram_user.id,
                                       reply_markup=reply_markup)


async def collection_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    await mes.reply_text("Выберите действие",
                         reply_markup=collection_menu_markup)


async def view_collection_list(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)
    coll = {}
    for x in user.collection:
        coll.update({x: {"card": cards_dict[x], "n": user.collection.count(x)}})

    response = "Ваша коллекция:\n\n"
    try:
        prev = coll[user.collection[0]]["card"]["type"]
    except IndexError:
        await mes.reply_text("У вас нет карточек. Чтобы получить их - перейдите в раздел Получение карт.",
                             reply_markup=collection_menu_markup)
        return

    for x in coll:
        card = coll[x]["card"]
        next_type_div = '\n' if card['type'] != prev else ''
        n = coll[x]["n"]
        n_of = f'({n} шт)' if n > 1 else ''

        response += (f"{next_type_div}"
                     f"{color_by_category[card['category']]} {card['name']} | {card['team']} {n_of}\n")
        prev = card["type"]

    await mes.reply_text(response,
                         reply_markup=collection_menu_markup,
                         parse_mode="HTML")
