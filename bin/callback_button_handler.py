import datetime
import re

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from bin.achievements import bot_check_achievements
from bin.anon_trade import (
    generate_trade_keyboard, anon_trade_select_desired,
    anon_trade_confirm_sell, anon_trade_buy_card_show_offers,
    anon_trade_choose_menu, generate_trade_offers_keyboard,
    anon_trade_show_my_offer, anon_trade_show_my_offers
)
from bin.battle import battle_init_menu, battle_confirm_choice, battle_init_game
from bin.coinflip import coinflip_result
from bin.collection import send_card_list, show_card, list_cards, get_collection_s, get_card_image
from bin.market import market_sell_list_menu, shop_menu
from bin.roll import roll_new_continue, roll_new
from lib.classes.user import User
from lib.init import BOT_INFO, logger
from lib.keyboard_markup import shop_inline_markup, generate_collection_keyboard
from lib.variables import (
    cards_dict, packs_prices, category_prices, sort_list,
    sort_keys_by, sort_list_transl, trades_log_chat_id, roll_cards_dict
)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = User.get(query.from_user)
    logger.log(BOT_INFO, f"{user.username} {query.data}")

    handlers = {
        "page_": handle_page,
        "market_page_": handle_market_page,
        "trade_page_": handle_trade_page,
        "anon_trade_sell_page_": handle_anon_trade_sell_page,
        "anon_trade_buy_page_": handle_anon_trade_buy_page,
        "anon_trade_view_offer_page_": handle_anon_trade_view_offer_page,
        "anon_trade_view_my_offers_page_": handle_anon_trade_view_my_offers_page,
        "c_": handle_card,
        "close_": handle_close,
        "market_close_": handle_market_close,
        "sell_": handle_sell,
        "pack_buy_": handle_pack_buy,
        "market_sell_card": handle_market_sell_card,
        "market_buy_card": handle_market_buy_card,
        "market_c": handle_market_card,
        "collection_sort_": handle_collection_sort,
        "trade_c_": handle_trade_card,
        "trade_confirm_": handle_trade_confirm,
        "trade_cancel": handle_trade_cancel,
        "coinflip_decline": handle_coinflip_decline,
        "coinflip_accept": handle_coinflip_accept,
        "coinflip_cancel": handle_coinflip_cancel,
        "ribbon_redeem": handle_ribbon_redeem,
        "anon_trade_add_": handle_anon_trade_add,
        "anon_trade_sell_c_": handle_anon_trade_sell,
        "anon_trade_confirm_sell_": handle_anon_trade_confirm_sell,
        "anon_trade_cancel_sell_": handle_anon_trade_cancel_sell,
        "anon_trade_close_sell_": handle_anon_trade_close_sell,
        "anon_trade_buy_c_": handle_anon_trade_buy,
        "anon_trade_view_buy_list": handle_anon_trade_view_buy_list,
        "anon_trade_close_buy": handle_anon_trade_close_buy,
        "anon_trade_view_offer_": handle_anon_trade_view_offer,
        "anon_trade_offer_confirm_": handle_anon_trade_offer_confirm,
        "anon_trade_my_offer_c_": handle_anon_trade_my_offer,
        "anon_trade_show_my_offers": handle_anon_trade_show_my_offers,
        "anon_trade_my_offer_remove_c_": handle_anon_trade_my_offer_remove,
        "anon_trade_my_offer_remove_confirm_c_": handle_anon_trade_my_offer_remove_confirm,
        "anon_trade_my_offers_close": handle_anon_trade_my_offers_close,
        "roll_": handle_roll_new_continue,
        "battle_page_": handle_battle_choice_page,
        "battle_select_c_": handle_battle_select,
        "pack_open_": handle_pack_open
    }

    for prefix, handler in handlers.items():
        if query.data.startswith(prefix):
            return await handler(update, context, query, user)

    if query.data == "noop":
        await query.answer()


async def handle_page(update, context, query, _):
    page = int(query.data.split("_")[1])
    await send_card_list(update, context, query.from_user, page, in_market=False, trade_receiver=0)


async def handle_battle_choice_page(update, context, query, _):
    page = int(query.data.split("_")[-1])
    context.user_data["battle_choice_page"] = page
    await battle_init_menu(update, context, page=page)


async def handle_market_page(update, context, query, _):
    page = int(query.data.split("_")[2])
    await send_card_list(update, context, query.from_user, page, in_market=True, trade_receiver=0)


async def handle_trade_page(update, context, query, _):
    page = int(query.data.split("_")[2])
    inline_keyboard = query.message.to_dict().get('reply_markup').get('inline_keyboard')
    receiver = re.search('trade_confirm_(.+)', inline_keyboard[-2][0]['callback_data']).group(1)
    await send_card_list(update, context, query.from_user, page, in_market=False, trade=True, trade_receiver=receiver)


async def handle_anon_trade_sell_page(_, context, query, __):
    page = int(query.data.split("_")[4])
    card_code = "c_" + re.search("anon_trade_sell_page_(.+)_c_(.+)", query.data).group(2)
    mode = query.data.split("_")[2]
    keyboard = generate_trade_keyboard(context, mode=mode, wts=card_code, page=page, user_id=query.from_user.id)
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def handle_anon_trade_buy_page(_, context, query, __):
    page = int(query.data.split("_")[4])
    context.user_data["page"] = page
    mode = query.data.split("_")[2]
    keyboard = generate_trade_keyboard(context, mode=mode, page=page, user_id=query.from_user.id)
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def handle_anon_trade_view_offer_page(_, context, query, user):
    page = int(query.data.split("_")[-1])
    context.user_data["anon_trade_page"] = page
    try:
        offers = context.user_data["anon_trade_offers"]
    except KeyError:
        await query.delete_message()
        return
    keyboard = generate_trade_offers_keyboard(context, offers=offers, page=page, user_id=user.id)
    if not keyboard:
        await query.answer("Ошибка")
        await query.delete_message()
        return
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def handle_anon_trade_view_my_offers_page(_, context, query, __):
    page = int(query.data.split("_")[-1])
    context.user_data["anon_trade_my_offers_page"] = page
    try:
        keyboard = generate_trade_offers_keyboard(context, type="my_offers",
                                                  offers=context.user_data["anon_trade_my_offers"], page=page)
    except KeyError:
        await query.delete_message()
        return
    if not keyboard:
        await query.answer("Ошибка")
        await query.delete_message()
        return
    await query.edit_message_reply_markup(reply_markup=keyboard)


async def handle_card(_, context, query, __):
    inline_keyboard = query.message.to_dict().get('reply_markup').get('inline_keyboard')
    page_index = next((i for i, item in enumerate(inline_keyboard[-1]) if item['callback_data'] == 'noop'), 0)
    page = int(inline_keyboard[-1][page_index]['text']) - 1
    try:
        await query.delete_message()
    except Exception as e:
        _ = e
        pass
    await show_card(query, context, in_market=False, page=page)


async def handle_close(update, context, query, _):
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


async def handle_market_close(update, context, query, _):
    await context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    await send_card_list(update, context, query.from_user, 0, in_market=True, trade_receiver=0)


async def handle_sell(update, context, query, user):
    if re.search("sell_c_(.+)_(.+)", query.data):
        card_code = "c_" + re.search("sell_c_(.+)_(.+)", query.data).group(1)
        page = int(re.search("sell_c_(.+)_(.+)", query.data).group(2))
        n_of_cards = user.collection.count(card_code)
        sell_n = context.user_data.get('sell_n', 1)
        card_category = cards_dict.get(card_code).get("category")
        card_name = cards_dict.get(card_code).get("name")
        card_price = category_prices.get(card_category)

        keyboard = [
            [InlineKeyboardButton("Да", callback_data=f"sell_confirm_{card_code}_{sell_n}_{page}")],
            [InlineKeyboardButton("Отменить", callback_data=f"sell_decline_{card_code}_{page}")]
        ]

        if n_of_cards > 1:
            decrease_button = InlineKeyboardButton("<", callback_data=f"sell_n_decrease_{card_code}_{page}")
            increase_button = InlineKeyboardButton(">", callback_data=f"sell_n_increase_{card_code}_{page}")
            quantity_button = InlineKeyboardButton(f"{sell_n}", callback_data=f"noop")

            quantity_row = []
            if sell_n > 1:
                quantity_row.append(decrease_button)
            else:
                quantity_row.append(InlineKeyboardButton("|", callback_data="noop"))
            quantity_row.append(quantity_button)
            if sell_n < n_of_cards:
                quantity_row.append(increase_button)
            else:
                quantity_row.append(InlineKeyboardButton("|", callback_data="noop"))

            keyboard.insert(0, quantity_row)

        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.edit_message_caption(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            caption=f"Вы уверены, что хотите продать {sell_n}x {card_name} за {card_price * sell_n} 🪙?\n\n"
                    f"(У вас осталось: {n_of_cards} шт.)\n\n",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        await query.answer()

    elif query.data.startswith("sell_decline_"):
        card_code = "c_" + re.search(r'sell_decline_c_(.+)_(.+)', query.data).group(1)
        page = int(re.search(r'sell_decline_c_(.+)_(.+)', query.data).group(2))
        await show_card(query, context, in_market=False, card_code=card_code, edit_message=True, page=page)

    elif query.data.startswith("sell_confirm_"):
        card_code, sell_n, page = re.search(r"sell_confirm_c_(.+)_(\d+)_(\d+)", query.data).groups()
        card_code = "c_" + card_code
        sell_n = int(sell_n)
        page = int(page)

        if card_code not in user.collection or user.collection.count(card_code) < sell_n:
            await query.answer("Ошибка: недостаточно карт")
            return

        card_category = cards_dict.get(card_code).get("category")
        # card_name = cards_dict.get(card_code).get("name")
        card_price = category_prices.get(card_category)

        for _ in range(sell_n):
            user.collection.remove(card_code)
        user.coins += card_price * sell_n
        user.write()

        await query.answer("Успешно продано!")
        context.user_data["sell_n"] = 1

        n_of_cards = user.collection.count(card_code)
        if n_of_cards == 0:
            await list_cards(update, context)
            await context.bot.delete_message(chat_id=user.id, message_id=query.message.message_id)
        else:
            # context.user_data['sell_n'] = 1  # Reset sell_n after successful sale
            await show_card(query, context, in_market=False, card_code=card_code, edit_message=True, page=page)

    elif query.data.startswith("sell_n_"):
        action, card_code, page = re.search(r"sell_n_(\w+)_c_(.+)_(\d+)", query.data).groups()
        card_code = "c_" + card_code
        page = int(page)
        n_of_cards = user.collection.count(card_code)
        sell_n = context.user_data.get('sell_n', 1)

        if action == "increase":
            sell_n = min(sell_n + 1, n_of_cards)
        elif action == "decrease":
            sell_n = max(sell_n - 1, 1)

        context.user_data['sell_n'] = sell_n
        await show_sell_confirmation(update, context, query, user, card_code, sell_n, page)


async def show_sell_confirmation(_, context, query, user, card_code, sell_n, page):
    n_of_cards = user.collection.count(card_code)
    card_category = cards_dict.get(card_code).get("category")
    card_name = cards_dict.get(card_code).get("name")
    card_price = category_prices.get(card_category)

    keyboard = [
        [InlineKeyboardButton("Да", callback_data=f"sell_confirm_{card_code}_{sell_n}_{page}")],
        [InlineKeyboardButton("Отменить", callback_data=f"sell_decline_{card_code}_{page}")]
    ]

    if n_of_cards > 1:
        decrease_button = InlineKeyboardButton("<", callback_data=f"sell_n_decrease_{card_code}_{page}")
        increase_button = InlineKeyboardButton(">", callback_data=f"sell_n_increase_{card_code}_{page}")
        quantity_button = InlineKeyboardButton(f"{sell_n}", callback_data=f"noop")

        quantity_row = []
        if sell_n > 1:
            quantity_row.append(decrease_button)
        else:
            quantity_row.append(InlineKeyboardButton("|", callback_data="noop"))
        quantity_row.append(quantity_button)
        if sell_n < n_of_cards:
            quantity_row.append(increase_button)
        else:
            quantity_row.append(InlineKeyboardButton("|", callback_data="noop"))

        keyboard.insert(0, quantity_row)

    if sell_n > n_of_cards:
        await query.answer()
        return

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.edit_message_caption(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        caption=f"Вы уверены, что хотите продать {sell_n}x {card_name} за {card_price * sell_n} 🪙?\n\n"
                f"(У вас осталось: {n_of_cards} шт.)\n\n",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    await query.answer()


async def handle_pack_buy(update, context, query, user):
    pack_type = re.search("pack_buy_(.+)", query.data).group(1)
    price = packs_prices.get(pack_type)

    if user.coins < price:
        await query.answer("Тебе не хватит денег даже на кружку пива. Иди зарабатывать.", show_alert=True)
        return

    user.coins -= price
    user.statistics["coins_spent"] += price
    user.rolls_available[pack_type] += 1
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


async def handle_market_sell_card(update, context, query, _):
    reply_markup = await generate_collection_keyboard(update, context, query.from_user.id, page=0, in_market=True)
    await context.bot.edit_message_text(chat_id=update.effective_user.id,
                                        message_id=query.message.message_id,
                                        text="Выберите карту:",
                                        reply_markup=reply_markup)


async def handle_market_buy_card(update, context, query, _):
    await query.answer()
    await market_sell_list_menu(update, context)


async def handle_market_card(_, context, query, __):
    await show_card(query, context, in_market=True)


async def handle_collection_sort(_, context, query, user):
    sorted_by = re.search("collection_sort_(.+)", query.data).group(1)
    coll = {z: {"card": cards_dict[z], "n": user.collection.count(z)} for z in user.collection}
    coll = dict(sorted(coll.items(), key=lambda x: sort_keys_by[sorted_by][x[1]['card'][sorted_by]]))

    next_sort_type = sort_list[(sort_list.index(sorted_by) + 1) % len(sort_list)]
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(sort_list_transl[sorted_by],
                                                               callback_data="collection_sort_" + next_sort_type)]])

    response = await get_collection_s(coll, user, context.bot, sorted_by)

    await context.bot.edit_message_text(chat_id=user.id,
                                        message_id=query.message.message_id,
                                        text=response,
                                        reply_markup=reply_markup,
                                        parse_mode="HTML")


async def handle_trade_card(update, context, query, user):
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


async def handle_trade_confirm(update, context, query, user):
    if not user.trade:
        await query.answer("Ошибка: не выбрано ни одной карты.")
        return
    try:
        receiver_id = int(re.search("trade_confirm_(.+)", query.data).group(1))
    except ValueError:
        receiver_id = re.search("trade_confirm_(.+)", query.data).group(1)
    receiver = User.get(None, receiver_id)
    receiver.collection += user.trade
    traded_cards_list = "\n".join(
        f"{cards_dict[c]['name']} {'| %s' % cards_dict[c]['team'] if cards_dict[c]['team'] else ''}" for c in
        user.trade)

    for c in user.trade:
        user.collection.remove(c)

    user.trade = []
    user.statistics["trades_complete"] += 1
    user.write()
    await bot_check_achievements(update, context)
    receiver.statistics["trades_complete"] += 1
    receiver.write()

    await context.bot.send_message(chat_id=user.id,
                                   text=f"<b>Передано пользователю {receiver.username}:</b>\n\n{traded_cards_list}",
                                   parse_mode="HTML")

    await context.bot.send_message(chat_id=receiver.id,
                                   text=f"<b>Получено от пользователя {user.username if user.username else user.id}:"
                                        f"</b>\n\n{traded_cards_list}",
                                   parse_mode="HTML")

    await context.bot.send_message(chat_id=trades_log_chat_id,
                                   text=f"<code>Trade @ {datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')}"
                                        f"\n</code><b>{user.username}</b> ({user.id}) --> <b>{receiver.username}</b> "
                                        f"({receiver.id})\n<blockquote expandable>{traded_cards_list}</blockquote>",
                                   parse_mode="HTML")

    await context.bot.delete_message(chat_id=user.id, message_id=query.message.message_id)
    await query.answer("Успешно!")


async def handle_trade_cancel(_, context, query, user):
    await context.bot.delete_message(chat_id=user.id, message_id=query.message.message_id)
    await query.answer("Отменено")


async def handle_coinflip_decline(_, context, query, user):
    opp = User.get(None, re.search("coinflip_decline_(.+)", query.data).group(1))
    resp_p1 = f"Пользователь {user.username} отклонил предложение игры."
    opp.coinflip = 0
    opp.write()

    try:
        await context.bot.delete_message(chat_id=user.id, message_id=query.message.message_id)
    except BadRequest:
        await query.answer("Игра не существует или уже завершена!")
    await context.bot.send_message(chat_id=opp.id, text=resp_p1)
    await query.answer("Отклонено")


async def handle_coinflip_accept(_, context, query, user):
    await query.answer()

    sender_id = int(re.search("coinflip_accept_(.+)_(.+)", query.data).group(1))
    await context.bot.send_message(chat_id=sender_id, text="🪙")
    await context.bot.send_message(chat_id=user.id, text="🪙")

    context.job_queue.run_once(coinflip_result, 3.5,
                               data=[{"query_data": query.data, "user_id": user.id}])

    try:
        await context.bot.delete_message(chat_id=user.id, message_id=query.message.message_id)
    except BadRequest:
        pass


async def handle_coinflip_cancel(_, context, query, user):
    pattern = re.compile("coinflip_cancel_(.+)_(.+)")
    opp_id, opp_mes_id = pattern.search(query.data).groups()
    try:
        await context.bot.delete_message(chat_id=opp_id, message_id=opp_mes_id)
    except BadRequest:
        await query.answer("Игра не существует или уже завершена!")
    user.coinflip = 0
    user.write()

    await context.bot.send_message(text="Успешно!", chat_id=user.id)

    try:
        await context.bot.delete_message(chat_id=user.id, message_id=query.message.message_id)
    except BadRequest:
        pass


async def handle_ribbon_redeem(_, context, query, user):
    for code in roll_cards_dict:
        user.collection = [c for c in user.collection if c != code]

    user.statistics["collectors_badge"] += 1
    user.write()

    await context.bot.delete_message(user.id, message_id=query.message.message_id)

    await context.bot.send_message(user.id,
                                   text="Поздравляем! Лента получена и отображается в вашем профиле, "
                                        "а карточки списаны. Может, ещё одну?")
    await query.answer()


async def handle_anon_trade_add(update, context, query, _):
    await query.answer()
    await query.delete_message()
    card_code = "c_" + re.search("anon_trade_add_c_(.+)_(.+)", query.data).group(1)
    page = re.search("anon_trade_add_c_(.+)_(.+)", query.data).group(2)
    await anon_trade_select_desired(update, context, wts=card_code, page=page)


async def handle_anon_trade_sell(update, context, query, _):
    await query.answer()
    wts = "c_" + re.search("anon_trade_sell_c_(.+)_c_(.+)", query.data).group(2)
    wtb = "c_" + re.search("anon_trade_sell_c_(.+)_c_(.+)", query.data).group(1)
    await anon_trade_confirm_sell(update, context, wts=wts, wtb=wtb)


async def handle_anon_trade_confirm_sell(update, context, query, user):
    await query.answer()
    wtb = "c_" + re.search("anon_trade_confirm_sell_c_(.+)_(.+)", query.data).group(2)
    wts = "c_" + re.search("anon_trade_confirm_sell_c_(.+)_c_(.+)", query.data).group(1)
    await query.delete_message()

    user.anon_trade.append({"wts": wts, "wtb": wtb})
    user.collection.remove(wts)
    user.write()

    resp = "Предложение создано успешно!"
    await context.bot.send_message(user.id, resp)

    await list_cards(update, context)


async def handle_anon_trade_cancel_sell(_, context, query, __):
    card_code = "c_" + query.data.split("_")[-1]
    await query.answer("Отменено")
    await query.delete_message()
    await show_card(query, context, in_market=False, card_code=card_code)


async def handle_anon_trade_close_sell(_, context, query, __):
    card_code = re.search("anon_trade_close_sell_(.+)", query.data).group(1)
    await query.delete_message()
    await show_card(query, context, in_market=False, card_code=card_code)


async def handle_anon_trade_buy(update, context, query, _):
    card_code = "c_" + re.search("anon_trade_buy_c_(.+)", query.data).group(1)
    await anon_trade_buy_card_show_offers(update, context, card_code=card_code)


async def handle_anon_trade_view_buy_list(update, context, query, user):
    await query.answer()
    try:
        page = context.user_data['anon_trade_page']
    except KeyError:
        context.user_data['anon_trade_page'] = 0
        page = 0
    await anon_trade_choose_menu(update, context, page=page, user_id=user.id)


async def handle_anon_trade_close_buy(*_, query, ___):
    await query.answer()
    await query.delete_message()


async def handle_anon_trade_view_offer(*_, query, user):
    await query.answer()
    receiver_id, wts, wtb = re.search("anon_trade_view_offer_(.+)_c_(.+)_c_(.+)", query.data).groups()
    wts = "c_" + wts
    wtb = "c_" + wtb

    if wtb not in user.collection:
        await query.answer("У вас нет этой карточки :(", show_alert=True)
        return

    resp = f"Вы согласны отдать карту {cards_dict[wtb]['name']} и получить карту {cards_dict[wts]['name']}?"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Да", callback_data=f"anon_trade_offer_confirm_{receiver_id}_{wts}_{wtb}")],
         [InlineKeyboardButton("Нет", callback_data=f"anon_trade_buy_{wts}")]])

    await query.edit_message_text(resp, reply_markup=keyboard)


async def handle_anon_trade_offer_confirm(update, context, query, user):
    receiver_id, wtb, wts = re.search("anon_trade_offer_confirm_(.+)_c_(.+)_c_(.+)", query.data).groups()
    wts = "c_" + wts
    wtb = "c_" + wtb

    receiver = User.get(None, int(receiver_id))
    try:
        user.collection.remove(wts)
        user.collection.append(wtb)
        receiver.anon_trade.remove({'wts': wtb, 'wtb': wts})
        receiver.collection.append(wts)
    except ValueError:
        await query.delete_message()
        return

    user.statistics["trades_complete"] += 1
    user.write()
    await bot_check_achievements(update, context)
    receiver.statistics["trades_complete"] += 1
    receiver.write()
    await bot_check_achievements(update, context, user=receiver)

    wtb_limited, wts_limited = wtb.startswith("c_9"), wts.startswith("c_9")

    wtb_card_pic_id = get_card_image(wtb, is_limited=wtb_limited)
    wts_card_pic_id = get_card_image(wts, is_limited=wts_limited)

    if wtb_limited:
        await context.bot.send_animation(user.id,
                                         animation=wtb_card_pic_id,
                                         caption=f"Успешно!\nПолучена карта: {cards_dict[wtb]['name']}.")
    else:
        await context.bot.send_photo(user.id,
                                     photo=wtb_card_pic_id,
                                     caption=f"Успешно!\nПолучена карта: {cards_dict[wtb]['name']}.")

    if wts_limited:
        await context.bot.send_animation(receiver.id,
                                         animation=wts_card_pic_id,
                                         caption=f"Кто-то обменялся с вами картой!\nПолучена карта: "
                                                 f"{cards_dict[wts]['name']}.")
    else:
        await context.bot.send_photo(receiver.id,
                                     photo=wts_card_pic_id,
                                     caption=f"Кто-то обменялся с вами картой!\nПолучена карта: "
                                             f"{cards_dict[wts]['name']}.")

    await context.bot.send_message(chat_id=trades_log_chat_id,
                                   text=f"<code>Trade @ {datetime.datetime.now().strftime('%d/%m/%y %H:%M:%S')}"
                                        f"\n</code><b>{user.username}</b> ({user.id}) --> <b>{receiver.username}</b> "
                                        f"({receiver.id})\n<blockquote expandable>{cards_dict[wts]['name']}"
                                        f"</blockquote>\n\n"
                                        f"<b>{receiver.username}</b> ({receiver.id}) --> <b>{user.username}</b> "
                                        f"({user.id})\n<blockquote expandable>{cards_dict[wtb]['name']}"
                                        f"</blockquote>",
                                   parse_mode="HTML")

    await query.answer()
    await anon_trade_choose_menu(update, context)


async def handle_anon_trade_my_offer(update, context, query, _):
    wts, wtb = re.search("anon_trade_my_offer_c_(.+)_c_(.+)", query.data).groups()
    wts = "c_" + wts
    wtb = "c_" + wtb

    await anon_trade_show_my_offer(update, context, wts=wts, wtb=wtb)


async def handle_anon_trade_show_my_offers(update, context, *_):
    page = context.user_data.get("anon_trade_my_offers_page", 0)
    await anon_trade_show_my_offers(update, context, page=page)


async def handle_anon_trade_my_offer_remove(*_, query, ___):
    wts, wtb = re.search("anon_trade_my_offer_remove_c_(.+)_c_(.+)", query.data).groups()
    resp = "Вы уверены, что хотите отменить предложение?"
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Да",
                                                           callback_data="anon_trade_my_offer_"
                                                                         f"remove_confirm_c_{wts}_c_{wtb}")],
                                     [InlineKeyboardButton("Нет",
                                                           callback_data="anon_trade_show_my_offers")]])
    await query.edit_message_text(resp,
                                  reply_markup=keyboard)


async def handle_anon_trade_my_offer_remove_confirm(update, context, query, user):
    page = context.user_data.get("page", 0)
    wts, wtb = re.search("anon_trade_my_offer_remove_confirm_c_(.+)_c_(.+)", query.data).groups()
    offer = {'wts': f'c_{wts}', 'wtb': f"c_{wtb}"}
    try:
        user.anon_trade.remove(offer)
        user.collection.append("c_" + wts)
        user.write()
    except ValueError:
        await query.answer("Предложения не существует!")
        await anon_trade_show_my_offers(update, context, page=page)
        return

    await anon_trade_show_my_offers(update, context, page=page)
    await query.answer("Предложение отменено успешно!")


async def handle_anon_trade_my_offers_close(_, context, query, __):
    try:
        await context.bot.delete_message(chat_id=query.from_user.id, message_id=query.message.message_id)
    except BadRequest:
        pass


async def handle_roll_new_continue(update, context, *_):
    await roll_new_continue(update, context)


async def handle_battle_select(update, context, *_):
    await battle_confirm_choice(update, context)


async def handle_choice_confirm(update, context, *_):
    await battle_init_game(update, context)


async def handle_pack_open(update, context, query, __):
    await query.answer()
    if query.message.photo:
        query.edit_message_reply_markup(reply_markup=None)
    else:
        await query.delete_message()
    await roll_new(update, context, pack_type=re.search("pack_open_(.+)", query.data).group(1))
