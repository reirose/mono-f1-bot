import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import ContextTypes, ConversationHandler

from lib.classes.user import User
from lib.keyboard_markup import collection_menu_markup, generate_collection_keyboard
from lib.messages_templates import get_message_text
from lib.variables import cards_dict, translation, sort_keys_by, sort_list, \
    sort_list_transl, category_color, cards_pics_cache


def get_card_image(card_id: str, is_limited: bool = False):
    try:
        if card_id in cards_pics_cache:
            return cards_pics_cache.get(card_id)
        return open(f"bin/img/{card_id}.mp4", "rb") if is_limited else open(f"bin/img/{card_id}.png", "rb")
    except FileNotFoundError:
        return open(f"bin/img/card.png", "rb")


async def show_card(query, context, in_market: bool, page: int = 0, edit_message: bool = False, **kwargs):
    user = User.get(query.from_user)
    card_code = kwargs.get("card_code") or f"c_{re.search('c_(.{3})', query.data).group(1)}"
    card = cards_dict[card_code]

    card_pic_id = get_card_image(card_code, is_limited=card["type"] == "limited" or card_code == "c_903")
    card_n = user.collection.count(card["code"])
    card_name = card["name"]
    card_team = card["team"]
    card_team = f"<b>Команда:</b> {card_team}\n" if card_team else ""
    card_category = translation[card["category"]]
    card_type = translation[card["type"]]
    card_description = card["description"]
    desc_str = f"<i>{card_description}</i>\n" if card_description else ""

    card_count = f'<i>Всего: {card_n} шт.</i>' if card_n > 1 else ''

    response = get_message_text("card_info",
                                card_name=card_name,
                                desc_str=desc_str,
                                card_team=card_team,
                                card_type=card_type,
                                card_category=card_category,
                                card_count=card_count)

    market_prefix = "market_" if in_market else ""
    reply_markup_buttons = [
        [InlineKeyboardButton("Продать", callback_data=f"{market_prefix}sell_{card['code']}_{page}")],
        [InlineKeyboardButton("Выбрать для трейда", callback_data=f"anon_trade_add_{card_code}_{page}")],
        [InlineKeyboardButton("Выставить на Маркете", callback_data=f"market_sell_card_{card_code}")],
        [InlineKeyboardButton("Закрыть", callback_data=f"{market_prefix}close_card_{page}")]
    ]
    reply_markup = InlineKeyboardMarkup(reply_markup_buttons)

    if edit_message:
        if card["type"] == "limited":
            await query.message.edit_caption(
                caption=response,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            await query.message.edit_caption(
                caption=response,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
    else:
        if card["type"] == "limited":
            await context.bot.send_animation(
                chat_id=query.message.chat.id,
                animation=card_pic_id,
                caption=response,
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            await context.bot.send_photo(
                chat_id=query.message.chat.id,
                photo=card_pic_id,
                caption=response,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

    await query.answer()


async def list_cards(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    try:
        page = int(context.user_data["page"])
        closed_card = context.user_data["closed_card"]
    except KeyError:
        page = 0
        closed_card = False
    await send_card_list(update, context, user, page, False, trade_receiver=0, closed_card=closed_card)


async def send_card_list(update: Update, context: ContextTypes.DEFAULT_TYPE,
                         telegram_user, page: int, in_market: bool,
                         trade_receiver: int, trade: bool = None, closed_card: bool = False) -> None:
    if not User.get(telegram_user).collection:
        await context.bot.send_message(text=get_message_text("no_cards_in_collection"),
                                       reply_markup=collection_menu_markup,
                                       chat_id=telegram_user.id)
        return
    reply_markup = await generate_collection_keyboard(update, context, telegram_user.id, page, in_market, trade=trade,
                                                      trade_receiver=trade_receiver)

    if update.callback_query and (not update.callback_query.data.startswith("sell_confirm_") and
                                  not update.callback_query.data == "close_card" and
                                  not update.callback_query.data.startswith("market_close_") and
                                  not update.callback_query.data.startswith("anon_trade_confirm_sell_") and
                                  not update.callback_query.data.startswith("market_confirm_sell_")):
        await update.callback_query.answer()
        if closed_card:
            await update.callback_query.delete_message()
            await context.bot.send_message(text="Ваш список карт:",
                                           chat_id=update.callback_query.message.chat.id,
                                           reply_markup=reply_markup)
            return

        await update.callback_query.edit_message_text("Ваш список карт:", reply_markup=reply_markup)
        return
    else:
        await context.bot.send_message(text="Ваш список карт:",
                                       chat_id=telegram_user.id,
                                       reply_markup=reply_markup)


async def collection_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    if not User.get(update.effective_user):
        return
    await mes.reply_text("Выберите действие",
                         reply_markup=collection_menu_markup)
    return ConversationHandler.END


async def get_collection_s(coll: dict, user: User, bot: Bot, sorted_by: str = 'category'):
    response = "Ваша коллекция:\n"
    # first = False
    try:
        prev = ''
    except IndexError:
        await bot.send_message(text=get_message_text("no_cards_in_collection"),
                               chat_id=user.id,
                               reply_markup=collection_menu_markup)
        return

    for x in coll:
        card = coll[x]["card"]
        next_type_div = f'<b>\n{translation[card[sorted_by]]}\n</b>' \
            if card[sorted_by] != prev else ''
        # next_type_div = f'<b>{"\n" if first else ""}{translation[card[sorted_by]]}\n</b>' \
        #     if card[sorted_by] != prev else ''
        # if next_type_div:
        #     first = True
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
        if z not in cards_dict:
            continue
        coll.update({z: {"card": cards_dict[z], "n": user.collection.count(z)}})

    coll = dict(sorted(coll.items(), key=lambda item: sort_keys_by[sorted_by][item[1]['card'][sorted_by]]))

    try:
        next_sort_type = sort_list[sort_list.index(sorted_by) + 1]
    except IndexError:
        next_sort_type = 'category'

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(sort_list_transl[sorted_by],
                                                               callback_data="collection_sort_" + next_sort_type)]])

    # await context.bot.send_message(chat_id=user.id,
    #                                text="Ваша коллекция:\n\n",
    #                                reply_markup=collection_menu_markup)

    response = await get_collection_s(coll, user, context.bot, sorted_by)
    if response == "Ваша коллекция:\n":
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Как-то тут пустовато 👀",
                                                                   callback_data="noop")]])

    await context.bot.send_message(chat_id=user.id,
                                   text=response,
                                   reply_markup=reply_markup,
                                   parse_mode="HTML")


async def collection_completeness(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    user = User.get(mes.from_user)
    completeness = int((len(set(user.collection)) / len(cards_dict)) * 100)
    resp = "Список карт в игре:\n"
    prev = ""
    for card in cards_dict:
        card_d = cards_dict[card]
        if prev != card_d["type"]:
            resp += "\n<b>" + translation[card_d["type"]] + "</b>\n"
            prev = card_d["type"]
        resp += f"{card_d['name']} {'☑️' if card in user.collection else ''}\n"

    resp += f"\n<i>Вы собрали {completeness}% всех карт в игре!</i>"

    await mes.reply_text(resp,
                         parse_mode="HTML")
