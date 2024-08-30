import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters

from bin.callback_button_handler import button_callback
from bin.collection import view_collection_list, collection_menu, list_cards
from bin.market import market_menu, market_place_card, conv_handler, buy_command
from bin.menu import menu
from bin.roll import roll, roll_menu
from bin.service_commands import start
from bin.other import other_menu
from bin.shop import shop_menu

from lib.init import TOKEN, client, BOT_INFO
from lib.filters import (other_button_filter, menu_button_filter, roll_menu_button_filter, roll_button_filter,
                         collection_menu_button_filter, show_card_button_filter, collection_list_button_filter,
                         dev_mode, shop_button_filter, me_button_filter, market_button_filter)
from lib.routines import update_cards, scheduler, update_free_roll

scheduler.start()

scheduler.add_job(update_cards, 'interval', hours=0.25)
scheduler.add_job(update_free_roll, 'cron', hour=20, minute=0, second=0)
scheduler.add_job(update_free_roll, 'cron', hour=8, minute=0, second=0)


async def print_test(update, _):
    user_input = update.message.text
    await update.message.reply_text(f"You entered: {user_input}")
    return ConversationHandler.END


def main():
    app: Application = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy_command, has_args=True))

    app.add_handler(MessageHandler(dev_mode & other_button_filter, other_menu))
    app.add_handler(MessageHandler(dev_mode & menu_button_filter, menu))
    app.add_handler(MessageHandler(dev_mode & me_button_filter, menu))
    app.add_handler(MessageHandler(dev_mode & roll_menu_button_filter, roll_menu))
    app.add_handler(MessageHandler(dev_mode & roll_button_filter, roll))
    app.add_handler(MessageHandler(dev_mode & collection_menu_button_filter, collection_menu))
    app.add_handler(MessageHandler(dev_mode & collection_list_button_filter, view_collection_list))
    app.add_handler(MessageHandler(dev_mode & show_card_button_filter, list_cards))
    app.add_handler(MessageHandler(dev_mode & shop_button_filter, shop_menu))
    app.add_handler(MessageHandler(dev_mode & market_button_filter, market_menu))

    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    update_cards()
    logging.log(BOT_INFO, "starting")
    main()
    client.close()
    logging.log(BOT_INFO, "exiting")
