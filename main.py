import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler

from bin.callback_button_handler import button_callback
from bin.coinflip import coinflip_conv_handler, abort, coinflip_menu
from bin.coinflip_pve import bot_coinflip_conv_handler
from bin.collection import view_collection_list, collection_menu, list_cards, collection_completeness
from bin.market import market_menu, conv_handler, buy_command, shop_menu
from bin.menu import menu, about_me, achievements
from bin.roll import roll, roll_menu
from bin.service_commands import start, dev_mode_change, unstuck, give_user
from bin.other import other_menu
from bin.packs_shop import packs_shop_menu
from bin.trade import trade_conv_handler

from lib.init import TOKEN, client, BOT_INFO
from lib.filters import (other_button_filter, menu_button_filter, roll_menu_button_filter, roll_button_filter,
                         collection_menu_button_filter, show_card_button_filter, collection_list_button_filter,
                         dev_mode, packs_shop_button_filter, me_button_filter, market_button_filter, not_banned_filter,
                         is_admin, all_cards_button_filter, shop_button_filter, coinflip_menu_button_filter)
from lib.routines import update_cards, scheduler, update_free_roll

scheduler.start()
scheduler.add_job(update_cards, 'interval', minutes=5)
scheduler.add_job(update_free_roll, 'cron', hour=20, minute=0, second=0)
scheduler.add_job(update_free_roll, 'cron', hour=8, minute=0, second=0)


def main():
    # объект всего приложения
    app: Application = Application.builder().token(TOKEN).build()

    # текстовые команды (через "/")
    app.add_handler(CommandHandler("start", start, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("dm", dev_mode_change))
    app.add_handler(CommandHandler("give", give_user, filters=is_admin))
    app.add_handler(CommandHandler("unstuck", unstuck, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("achievements", achievements, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("buy", buy_command, has_args=True, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("coinflip_cancel", abort, filters=dev_mode & not_banned_filter))

    # обработчики текстовых сообщений (для кнопок)
    app.add_handler(MessageHandler(dev_mode & other_button_filter & not_banned_filter, other_menu))
    app.add_handler(MessageHandler(dev_mode & menu_button_filter & not_banned_filter, menu))
    app.add_handler(MessageHandler(dev_mode & me_button_filter & not_banned_filter, about_me))
    app.add_handler(MessageHandler(dev_mode & roll_menu_button_filter & not_banned_filter, roll_menu))
    app.add_handler(MessageHandler(dev_mode & roll_button_filter & not_banned_filter, roll))
    app.add_handler(MessageHandler(dev_mode & collection_menu_button_filter & not_banned_filter, collection_menu))
    app.add_handler(MessageHandler(dev_mode & collection_list_button_filter & not_banned_filter, view_collection_list))
    app.add_handler(MessageHandler(dev_mode & show_card_button_filter & not_banned_filter, list_cards))
    app.add_handler(MessageHandler(dev_mode & packs_shop_button_filter & not_banned_filter, packs_shop_menu))
    app.add_handler(MessageHandler(dev_mode & shop_button_filter & not_banned_filter, shop_menu))
    app.add_handler(MessageHandler(dev_mode & market_button_filter & not_banned_filter, market_menu))
    app.add_handler(MessageHandler(dev_mode & all_cards_button_filter & not_banned_filter, collection_completeness))
    app.add_handler(MessageHandler(dev_mode & coinflip_menu_button_filter & not_banned_filter, coinflip_menu))

    # обработчик беседы (для продажи)
    app.add_handler(conv_handler)
    app.add_handler(trade_conv_handler)
    app.add_handler(coinflip_conv_handler)
    app.add_handler(bot_coinflip_conv_handler)
    # обработчик инлайн кнопок
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    update_cards()
    logging.log(BOT_INFO, "starting")
    main()
    client.close()
    logging.log(BOT_INFO, "exiting")
