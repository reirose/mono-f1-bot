import random
import re
import uuid

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters, \
    CommandHandler

from bin.menu import menu
from lib.classes.user import User
from lib.init import MARKET_COLLECTION
from lib.keyboard_markup import shop_menu_markup
from lib.variables import cards_dict


async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    telegram_user = update.effective_user
    user = User.get(telegram_user)

    offer = MARKET_COLLECTION.find_one({"id": context.args[0]})

    if not offer:
        await mes.reply_text("Предложения не существует")
        return

    if user.coins < offer["price"]:
        await mes.reply_text("Недостаточно монет.")
        return

    user.coins -= offer["price"]
    user.collection.append(offer["code"])
    user.statistics["coins_spent"] += offer["price"]
    user.write()
    seller = User.get(user=None, update=offer["seller"])
    seller.coins += offer["price"]
    seller.write()
    MARKET_COLLECTION.delete_one({"id": offer["id"]})
    await mes.reply_text(f"Вы купили карту {cards_dict[offer['code']]['name']} за {offer['price']}")
    await context.bot.send_message(chat_id=seller.id,
                                   text=f"У вас купили карту {cards_dict[offer['code']]['name']} за {offer['price']}!")


async def shop_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(text="🛒",
                                   chat_id=update.callback_query.from_user.id if update.callback_query
                                   else update.message.from_user.id,
                                   reply_markup=shop_menu_markup)


async def market_menu(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Продать карту", callback_data="market_sell_card")],
                                         [InlineKeyboardButton("Купить карту", callback_data="market_buy_card")],
                                         [InlineKeyboardButton("Закрыть", callback_data="close_market")]])

    await mes.reply_text("Здеся вы можете продаватб свои и покупатб чцжие карты ъх",
                         reply_markup=reply_markup)


async def entry(update, _):
    query = update.callback_query
    card_code = re.match("market_sell_(.+)", query.data).group(1)
    user = User.get(query.from_user)
    user.market = card_code
    user.write()
    await query.answer()
    await update.effective_chat.send_message("Введите цену.\n\nДля отмены операции нажмите /cancel")
    return "market_sell_card"


async def market_place_card(update: Update, _: ContextTypes.DEFAULT_TYPE):
    mes = update.message
    try:
        price = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Неверный ввод.")
        # await menu(update, _)
        return "market_sell_card"

    if price <= 0:
        await update.message.reply_text("Неверный ввод.")
        # await menu(update, _)
        return "market_sell_card"

    user = User.get(update.effective_user)
    card_code = user.market
    user.collection.remove(card_code)
    user.market = ""
    user.write()
    op_id = uuid.uuid4().hex[-8:]
    MARKET_COLLECTION.insert_one({"id": op_id,
                                  "code": card_code,
                                  "price": price,
                                  "seller": user.username})

    response = f"Удачно! Код операции: {op_id}"
    await mes.reply_text(response,
                         reply_markup=shop_menu_markup)
    return ConversationHandler.END


async def market_sell_list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = User.get(update.effective_user)
    offers = list(MARKET_COLLECTION.find(filter={}))
    available_offers = []
    for x in offers:
        if x["price"] > user.coins:
            continue
        available_offers.append(x)

    random.shuffle(available_offers)
    response = "\n".join([f"{cards_dict[x['code']]['name']} - {x['price']} - <code>{x['id']}</code>"
                          for x in available_offers[:20 if len(available_offers) >= 20 else len(available_offers)]])
    if response:
        response += "\n<i>Для покупки карты скопируйте код и введите /buy код</i>"
    else:
        response = "Сейчас нет доступных предложений.\n"

    await context.bot.send_message(text=response,
                                   chat_id=update.effective_user.id,
                                   reply_markup=shop_menu_markup,
                                   parse_mode="HTML")


conv_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(entry, pattern=r'^market_sell_c_\d{3}$|^market_buy_\S{12}')],
    states={
        "market_sell_card": [MessageHandler(filters.TEXT & ~filters.COMMAND, market_place_card)],
    },
    fallbacks=[CommandHandler("cancel", menu)]
)
