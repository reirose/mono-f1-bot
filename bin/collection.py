import re
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from lib.classes.user import User
from lib.keyboard_markup import collection_menu_markup, generate_collection_keyboard
from lib.variables import cards_dict, translation, sort_keys_by, sort_list, \
    sort_list_transl, category_color


async def show_card(query, context, in_market: bool):
    user_collection = User.get(query.from_user).collection
    card = cards_dict.get(f"c_{re.search('c_(.{3})', query.data).group(1)}")
    # card_pic_id = ("AgACAgQAAxkBAAIMP2bKLDHHQSdb4-"
    #                "4qJpG9WTW7k8QtAAK0wTEbmxtZUuGYL8YF6ayLAQADAgADeAADNQQ")  # TODO: сделать оформление из файла
    try:
        card_pic_id = open(f"bin/img/{card['code']}.png", "rb")
    except FileNotFoundError:
        card_pic_id = ("AgACAgQAAxkBAAIMP2bKLDHHQSdb4-"
                       "4qJpG9WTW7k8QtAAK0wTEbmxtZUuGYL8YF6ayLAQADAgADeAADNQQ")
    card_name = card["name"]
    card_team = card["team"]
    card_team = f"Команда: {card_team}\n" if card_team else ""
    card_category = translation[card["category"]]
    card_type = translation[card["type"]]
    card_n = user_collection.count(card["code"])
    card_description = card["description"]
    desc_str = f"<i>{card_description}</i>\n" if card_description else ""
    response = (f"<b>{card_name}</b>\n"
                f"{desc_str}\n"
                f"{card_team}"
                f"Тип карты: {card_type}\n"
                f"Редкость: {card_category}\n\n"
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
    await send_card_list(update, context, user, page, False, trade_receiver=0)


async def send_card_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         telegram_user, page: int, in_market: bool,
                         trade_receiver: int, trade: bool = None) -> None:
    if not User.get(telegram_user).collection:
        await context.bot.send_message(text="У вас нет карточек. Чтобы получить их - "
                                            "перейдите в раздел Получение карт.",
                                       reply_markup=collection_menu_markup,
                                       chat_id=telegram_user.id)
        return
    reply_markup = await generate_collection_keyboard(update, context, telegram_user.id, page, in_market, trade=trade,
                                                      trade_receiver=trade_receiver)

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


async def get_collection_s(coll: dict, user: User, bot: Bot, sorted_by: str = 'category'):
    response = ""
    try:
        prev = ''
    except IndexError:
        await bot.send_message(text="У вас нет карточек. Чтобы получить их - перейдите в раздел Получение карт.",
                               chat_id=user.id,
                               reply_markup=collection_menu_markup)
        return

    for x in coll:
        card = coll[x]["card"]
        next_type_div = f'<b>\n{translation[card[sorted_by]]}\n</b>' if card[sorted_by] != prev else ''
        n = coll[x]["n"]
        n_of = f'({n} шт)' if n > 1 else ''

        response += (f"{next_type_div}"
                     f"{category_color[card['category']]}{card['name']} "
                     f"{'| ' + card['team'] if card['team'] else ''} {n_of}\n")
        prev = card[sorted_by]

    return response


async def view_collection_list(update: Update, context: ContextTypes.DEFAULT_TYPE, sorted_by: str = "category"):
    telegram_user = update.effective_user
    user = User.get(telegram_user)
    coll = {}
    for z in user.collection:
        coll.update({z: {"card": cards_dict[z], "n": user.collection.count(z)}})

    coll = dict(sorted(coll.items(), key=lambda item: sort_keys_by[sorted_by][item[1]['card'][sorted_by]]))

    try:
        next_sort_type = sort_list[sort_list.index(sorted_by) + 1]
    except IndexError:
        next_sort_type = 'category'

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(sort_list_transl[sorted_by],
                                                               callback_data="collection_sort_" + next_sort_type)]])

    await context.bot.send_message(chat_id=user.id,
                                   text="Ваша коллекция:\n\n",
                                   reply_markup=collection_menu_markup)

    response = await get_collection_s(coll, user, context.bot, sorted_by)

    await context.bot.send_message(chat_id=user.id,
                                   text=response,
                                   reply_markup=reply_markup,
                                   parse_mode="HTML")


async def collection_completeness(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    user = User.get(mes.from_user)
    resp = "Список карт в игре:\n"
    prev = ""
    for card in cards_dict:
        card_d = cards_dict[card]
        if prev != card_d["type"]:
            resp += "\n<b>" + translation[card_d["type"]] + "</b>\n"
            prev = card_d["type"]
        resp += f"{card_d['name']} {'✅' if card in user.collection else ''}\n"

    await mes.reply_text(resp,
                         parse_mode="HTML")
