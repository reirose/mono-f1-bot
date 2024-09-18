import datetime
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from bin.collection import send_card_list, show_card, list_cards, get_collection_s
from bin.market import market_sell_list_menu
from bin.other import other_menu
from lib.classes.user import User
from lib.keyboard_markup import shop_inline_markup, generate_collection_keyboard
from lib.variables import cards_dict, packs_prices, category_prices, sort_list, sort_keys_by, sort_list_transl


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_user = query.from_user
    user = User.get(telegram_user)
    print(f"{datetime.datetime.now().strftime('%H:%M:%S')} -- {user.username} -- {query.data}")

    if query.data.startswith("page_"):
        page = int(query.data.split("_")[1])
        await send_card_list(update, context, telegram_user, page, in_market=False)

    if query.data.startswith("market_page_"):
        page = int(query.data.split("_")[2])
        await send_card_list(update, context, telegram_user, page, in_market=True)

    elif query.data.startswith("c_"):
        await show_card(query, context, in_market=False)

    elif query.data.startswith("close_"):
        await context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        if "card" in query.data:
            await list_cards(update, context)
        elif "market" in query.data:
            await other_menu(update, context)

    elif query.data.startswith("market_close_"):
        await context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        await send_card_list(update, context, telegram_user, 0, in_market=True)

    elif query.data == "noop":
        await query.answer()

    elif query.data.startswith("sell_") and query.data.count("_") == 2:
        card_code = re.search("sell_(.+)", query.data).group(1)
        n_of_cards = user.collection.count(card_code)
        card_category = cards_dict.get(card_code).get("category")
        card_name = cards_dict.get(card_code).get("name")
        card_price = category_prices.get(card_category)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Да",
                                                                   callback_data=f"sell_confirm_"
                                                                                 f"{card_code}")],
                                             [InlineKeyboardButton("Отменить",
                                                                   callback_data=f"sell_decline_"
                                                                                 f"{card_code}")]])
        await context.bot.edit_message_caption(chat_id=query.message.chat.id,
                                               message_id=query.message.message_id,
                                               caption=f"Вы уверены, что хотите продать {card_name} за "
                                                       f"{card_price} 🪙?\n\n"
                                                       f"(У вас осталось: {n_of_cards} шт.)\n\n"
                                                       f"<i>Осуществляется быстрая продажа карты. Для продажи карты"
                                                       f" другим пользователям перейдите в раздел Маркет (Другое)</i>",
                                               reply_markup=reply_markup,
                                               parse_mode="HTML")
        await query.answer()

    elif query.data.startswith("sell_decline_"):
        await context.bot.delete_message(chat_id=user.id,
                                         message_id=query.message.message_id)
        await show_card(query, context, in_market=False)

    elif query.data.startswith("sell_confirm_"):
        card_code = re.search("sell_confirm_(.+)", query.data).group(1)
        card_category = cards_dict.get(card_code).get("category")
        card_name = cards_dict.get(card_code).get("name")
        card_price = category_prices.get(card_category)
        if card_code not in user.collection:
            await query.answer("Ошибка")
            return

        user.collection.remove(card_code)
        user.coins += card_price
        user.write()
        await query.answer("Успешно!")

        if card_code not in user.collection:
            await list_cards(update, context)
            await context.bot.delete_message(chat_id=user.id,
                                             message_id=query.message.message_id)
            return

        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Да",
                                                                   callback_data=f"sell_confirm_"
                                                                                 f"{card_code}")],
                                             [InlineKeyboardButton("Отменить",
                                                                   callback_data=f"sell_decline_"
                                                                                 f"{card_code}")]])
        n_of_cards = user.collection.count(card_code)
        await context.bot.edit_message_caption(chat_id=query.message.chat.id,
                                               message_id=query.message.message_id,
                                               caption=f"Вы уверены, что хотите продать {card_name} за "
                                                       f"{card_price} 🪙?\n\n"
                                                       f"(У вас осталось: {n_of_cards} шт.)",
                                               reply_markup=reply_markup)

    elif query.data.startswith("pack_buy_"):
        quant = int(re.search("pack_buy_(.+)", query.data).group(1))
        price = packs_prices.get(quant)

        if user.coins < price:
            await query.answer("Тебе не хватит денег даже на кружку пива. Иди зарабатывать.", show_alert=True)
            return

        user.coins -= price
        user.rolls_available += quant
        user.write()
        await query.answer("Успешно!")

        response = ("Тут можно приобрести дополнительные паки для открытия.\n\n"
                    f"Ваши монеты: {user.coins} шт.")
        reply_markup = shop_inline_markup

        await context.bot.edit_message_text(chat_id=user.id,
                                            message_id=query.message.message_id,
                                            text=response,
                                            reply_markup=reply_markup)

    elif query.data == "market_sell_card":
        reply_markup = await generate_collection_keyboard(update, context, telegram_user.id, page=0, in_market=True)
        await context.bot.edit_message_text(chat_id=update.effective_user.id,
                                            message_id=query.message.message_id,
                                            text="Выберите карту:",
                                            reply_markup=reply_markup)

    elif query.data == "market_buy_card":
        await query.answer()
        await market_sell_list_menu(update, context)

    elif query.data.startswith("market_c"):
        await show_card(query, context, in_market=True)

    elif query.data.startswith("collection_sort_"):
        sorted_by = re.search("collection_sort_(.+)", query.data).group(1)
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

        response = await get_collection_s(coll, user, context.bot, sorted_by)

        await context.bot.edit_message_text(chat_id=user.id,
                                            message_id=query.message.message_id,
                                            text=response,
                                            reply_markup=reply_markup,
                                            parse_mode="HTML")
