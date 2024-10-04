import datetime
import logging
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bin.achievements import bot_check_achievements
from bin.anon_trade import generate_trade_keyboard, anon_trade_select_desired, \
    anon_trade_confirm_sell, anon_trade_buy_card_show_offers, anon_trade_choose_menu
from bin.coinflip import coinflip_result
from bin.collection import send_card_list, show_card, list_cards, get_collection_s
from bin.market import market_sell_list_menu, shop_menu
from lib.classes.user import User
from lib.init import BOT_INFO
from lib.keyboard_markup import shop_inline_markup, generate_collection_keyboard
from lib.variables import cards_dict, packs_prices, category_prices, sort_list, sort_keys_by, sort_list_transl, \
    trades_log_chat_id, roll_cards_dict


def find_noop_index(data):
    for index, item in enumerate(data):
        if item.get('callback_data') == 'noop':
            return index


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    telegram_user = query.from_user
    user = User.get(telegram_user)
    logging.log(BOT_INFO, f"{user.username} {query.data}")

    if query.data.startswith("page_"):
        page = int(query.data.split("_")[1])
        await send_card_list(update, context, telegram_user, page, in_market=False, trade_receiver=0)

    if query.data.startswith("market_page_"):
        page = int(query.data.split("_")[2])
        await send_card_list(update, context, telegram_user, page, in_market=True, trade_receiver=0)

    if query.data.startswith("trade_page_"):
        page = int(query.data.split("_")[2])
        inline_keyboard = query.message.to_dict().get('reply_markup').get('inline_keyboard')
        receiver = re.search('trade_confirm_(.+)', inline_keyboard[-2][0]['callback_data']).group(1)
        await send_card_list(update, context, telegram_user, page, in_market=False, trade=True,
                             trade_receiver=receiver)

    if query.data.startswith("anon_trade_sell_page_"):
        page = int(query.data.split("_")[4])
        card_code = "c_" + re.search("anon_trade_sell_page_(.+)_c_(.+)", query.data).group(2)
        context.user_data["page"] = page
        mode = query.data.split("_")[2]
        keyboard = generate_trade_keyboard(context, mode=mode, wts=card_code)
        await query.edit_message_reply_markup(reply_markup=keyboard)

    if query.data.startswith("anon_trade_buy_page_"):
        page = int(query.data.split("_")[4])
        context.user_data["page"] = page
        mode = query.data.split("_")[2]
        keyboard = generate_trade_keyboard(context, mode=mode)
        await query.edit_message_reply_markup(reply_markup=keyboard)

    elif query.data.startswith("c_"):
        inline_keyboard = query.message.to_dict().get('reply_markup').get('inline_keyboard')
        page_index = 0
        for i, item in enumerate(inline_keyboard[-1]):
            if item['callback_data'] == 'noop':
                page_index = i
                break

        page = int(inline_keyboard[-1][page_index]['text']) - 1
        await show_card(query, context, in_market=False, page=page)

    elif query.data.startswith("close_"):
        if "card" in query.data:
            context.user_data['page'] = query.data.split("_")[-1]
            context.user_data["closed_card"] = True
            await list_cards(update, context)
        elif "market" in query.data:
            await shop_menu(update, context)
        try:
            await context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        except BadRequest:
            pass

    elif query.data.startswith("market_close_"):
        await context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
        await send_card_list(update, context, telegram_user, 0, in_market=True, trade_receiver=0)

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
        if card_code not in user.collection:
            context.bot.delete_message(chat_id=user.id,
                                       message_id=query.message.message_id)
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
        user.statistics["coins_spent"] += price
        user.rolls_available += quant
        user.write()
        await bot_check_achievements(update, context)
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

        coll = dict(sorted(coll.items(), key=lambda x: sort_keys_by[sorted_by][x[1]['card'][sorted_by]]))

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

    elif query.data.startswith("trade_c_"):
        await query.answer()
        card_code = re.search("trade_(.+)", query.data).group(1)
        if card_code in user.trade:
            user.trade.remove(card_code)
        else:
            user.trade.append(card_code)
        user.write()

        inline_keyboard = query.message.to_dict().get('reply_markup').get('inline_keyboard')
        receiver = re.search('trade_confirm_(.+)', inline_keyboard[-2][0]['callback_data']).group(1)
        page_index = next((i for i, item in enumerate(inline_keyboard[-3]) if item['callback_data'] == 'noop'))
        page = int(inline_keyboard[-3][page_index]['text']) - 1
        keyboard = await generate_collection_keyboard(update, context, user.id, page=page,
                                                      in_market=False, trade=True, trade_receiver=receiver)
        await context.bot.edit_message_reply_markup(chat_id=query.message.chat.id,
                                                    message_id=query.message.message_id,
                                                    reply_markup=keyboard)

    elif query.data.startswith("trade_confirm_"):
        if not user.trade:
            await query.answer("Ошибка: не выбрано ни одной карты.")
            return
        try:
            receiver_id = int(query.data.split("_")[-1])
        except ValueError:
            receiver_id = re.search("trade_confirm_(.+)", query.data).group(1)
        receiver = User.get(None, receiver_id)
        receiver.collection += user.trade
        traded_cards_list = ""
        for i, c in enumerate(user.trade):
            card = cards_dict[c]
            traded_cards_list += f"{card['name']} {'| %s' % card['team'] if card['team'] else ''}\n"
            user.collection.remove(c)

        user.trade = []
        user.statistics["trades_complete"] += 1
        user.write()
        await bot_check_achievements(update, context)
        receiver.statistics["trades_complete"] += 1
        receiver.write()

        await context.bot.send_message(chat_id=user.id,
                                       text="<b>Передано пользователю %s:</b>\n\n%s" % (
                                           receiver.username, traded_cards_list),
                                       parse_mode="HTML")

        await context.bot.send_message(chat_id=receiver.id,
                                       text="<b>Получено от пользователя %s:</b>\n\n%s" % (
                                           user.username if user.username else user.id, traded_cards_list),
                                       parse_mode="HTML")

        await context.bot.send_message(chat_id=trades_log_chat_id,
                                       text=f"<code>Trade @ "
                                            f"{datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')}\n</code>"
                                            f"<b>{user.username}</b> ({user.id}) --> "
                                            f"<b>{receiver.username}</b> ({receiver.id})\n"
                                            f"<blockquote expandable>{traded_cards_list}</blockquote>",
                                       parse_mode="HTML")

        await context.bot.delete_message(chat_id=user.id,
                                         message_id=query.message.message_id)
        await query.answer("Успешно!")

    elif query.data == "trade_cancel":
        await context.bot.delete_message(chat_id=user.id,
                                         message_id=query.message.message_id)
        await query.answer("Отменено")

    elif query.data.startswith("coinflip_decline"):
        opp = User.get(None, re.search("coinflip_decline_(.+)", query.data)).group(1)
        resp_p1 = f"Пользователь {user.username} отклонил предложение игры."
        opp.coinflip = 0
        opp.write()

        try:
            await context.bot.delete_message(chat_id=user.id,
                                             message_id=query.message.message_id)
        except BadRequest:
            await query.answer("Игра не существует или уже завершена!")
        await context.bot.send_message(chat_id=opp.id,
                                       text=resp_p1)
        await query.answer("Отклонено")

    elif query.data.startswith("coinflip_accept"):
        await query.answer()

        sender_id = int(re.search("coinflip_accept_(.+)_(.+)", query.data).group(1))
        await context.bot.send_message(chat_id=sender_id,
                                       text="🪙")

        await context.bot.send_message(chat_id=user.id,
                                       text="🪙")

        context.job_queue.run_once(coinflip_result, 3.5,
                                   data=[{"query_data": query.data,
                                          "user_id": user.id}])

        try:
            await context.bot.delete_message(chat_id=user.id,
                                             message_id=query.message.message_id)
        except BadRequest:
            pass

    elif query.data.startswith("coinflip_cancel"):
        pattern = re.compile("coinflip_cancel_(.+)_(.+)")
        opp_id = pattern.search(query.data).group(1)
        opp_mes_id = pattern.search(query.data).group(2)
        try:
            await context.bot.delete_message(chat_id=opp_id,
                                             message_id=opp_mes_id)
        except BadRequest:
            await query.answer("Игра не существует или уже завершена!")
        user.coinflip = 0
        user.write()

        await context.bot.send_message(text="Успешно!",
                                       chat_id=user.id)

        try:
            await context.bot.delete_message(chat_id=user.id,
                                             message_id=query.message.message_id)
        except BadRequest:
            pass

    elif query.data == "ribbon_redeem":
        for code, _ in roll_cards_dict.items():
            for __ in range(user.collection.count(code)):
                user.collection.remove(code)

        user.statistics["collectors_badge"] += 1
        user.write()

        await context.bot.delete_message(user.id,
                                         message_id=query.message.message_id)

        await context.bot.send_message(user.id,
                                       text="Поздравляем! Лента получена и отображается в вашем, а карточки списаны. "
                                            "Может, ещё одну?")
        await query.answer()

    elif query.data.startswith("anon_trade_add_"):
        await query.answer()
        await query.delete_message()
        card_code = "c_" + re.search("anon_trade_add_c_(.+)_(.+)", query.data).group(1)
        page = re.search("anon_trade_add_c_(.+)_(.+)", query.data).group(2)
        context.user_data["wts"] = card_code
        context.user_data["page"] = page
        await anon_trade_select_desired(update, context)

    elif query.data.startswith("anon_trade_sell_c_"):
        await query.answer()
        wts = "c_" + re.search("anon_trade_sell_c_(.+)_c_(.+)", query.data).group(2)
        wtb = "c_" + re.search("anon_trade_sell_c_(.+)_c_(.+)", query.data).group(1)
        context.user_data["wtb"] = wtb
        context.user_data["wts"] = wts
        await anon_trade_confirm_sell(update, context)

    elif query.data.startswith("anon_trade_confirm_sell_"):
        await query.answer()
        wtb = "c_" + re.search("anon_trade_confirm_sell_c_(.+)_(.+)", query.data).group(2)
        wts = "c_" + re.search("anon_trade_confirm_sell_c_(.+)_c_(.+)", query.data).group(1)
        await query.delete_message()

        user.anon_trade.append({"wts": wts, "wtb": wtb})
        user.collection.remove(wts)
        user.write()

        resp = "Предложение создано успешно!"
        await context.bot.send_message(user.id,
                                       resp)

        await list_cards(update, context)

    elif query.data == "anon_trade_cancel_sell":
        await query.answer("Отменено")
        await query.delete_message()

    elif query.data.startswith("anon_trade_close_sell_"):
        card_code = re.search("anon_trade_close_sell_(.+)", query.data).group(1)
        context.user_data["card_code"] = card_code
        await show_card(query, context, in_market=False)

    elif query.data.startswith("anon_trade_buy_c_"):
        card_code = "c_" + re.search("anon_trade_buy_c_(.+)", query.data).group(1)
        context.user_data["card_code"] = card_code
        await anon_trade_buy_card_show_offers(update, context)

    elif query.data.startswith("anon_trade_view_buy_list"):
        await query.answer()
        context.user_data["page"] = 0
        await anon_trade_choose_menu(update, context)
