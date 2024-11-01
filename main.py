import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from bin.anon_trade import anon_trade_choose_menu, anon_trade_main_menu, anon_trade_show_my_offers
from bin.callback_button_handler import button_callback
from bin.coinflip import coinflip_conv_handler, abort, coinflip_menu
from bin.coinflip_pve import bot_coinflip_conv_handler
from bin.collection import view_collection_list, collection_menu, list_cards, collection_completeness
from bin.market import shop_menu, market_offers_menu, market_menu_new, conv_handler, market_show_my_offers_list
from bin.menu import menu, achievements
from bin.pitstop import pitstop_conv_handler, pitstop_menu
from bin.roll import roll_menu, packs_menu
from bin.service_commands import dev_mode_change, unstuck, give_user, ribbon_info, get_logs, update_github, \
    handle_promo_link, generate_promo_link
from bin.other import other_menu
from bin.packs_shop import packs_shop_menu
from bin.settings import settings_menu
from bin.trade import trade_conv_handler

from lib.init import TOKEN, client, BOT_INFO
from lib.filters import (other_button_filter, menu_button_filter, roll_menu_button_filter, roll_button_filter,
                         collection_menu_button_filter, show_card_button_filter, collection_list_button_filter,
                         dev_mode, packs_shop_button_filter, not_banned_filter,
                         is_admin, all_cards_button_filter, shop_button_filter, coinflip_menu_button_filter,
                         anon_trade_button_filter, offers_button_filter, my_offers_button_filter,
                         market_offers_button_filter, market_button_filter, market_my_offers_button_filter,
                         pitstop_button_filter, settings_button_filter)
from lib.routines import update_cards, scheduler, update_free_roll, clear_logs, notify_free_pack, async_scheduler, \
    check_trades_market_expiration

scheduler.start()
async_scheduler.start()
scheduler.add_job(update_cards, 'interval', minutes=5)
scheduler.add_job(update_free_roll, 'cron', hour=8, minute=0, second=0)
scheduler.add_job(update_free_roll, 'cron', hour=20, minute=0, second=0)
async_scheduler.add_job(notify_free_pack, 'cron', hour=8, minute=0, second=0)
async_scheduler.add_job(notify_free_pack, 'cron', hour=20, minute=0, second=0)
async_scheduler.add_job(check_trades_market_expiration, 'cron', hour=0, minute=0, second=0)
scheduler.add_job(clear_logs, 'interval', hours=1)


def main():
    # объект всего приложения
    app: Application = Application.builder().token(TOKEN).build()

    # текстовые команды (через "/")
    app.add_handler(CommandHandler("start", handle_promo_link,
                                   filters=dev_mode & not_banned_filter & filters.Regex("promo_(.+)")))
    # app.add_handler(CommandHandler("start", start, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("dm", dev_mode_change))
    app.add_handler(CommandHandler("give", give_user, filters=is_admin))
    app.add_handler(CommandHandler("generate_promo", generate_promo_link, filters=is_admin, has_args=True))
    app.add_handler(CommandHandler("get_logs", get_logs, filters=is_admin, has_args=True))
    app.add_handler(CommandHandler("packs", packs_menu, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("unstuck", unstuck, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("achievements", achievements, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("coinflip_cancel", abort, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("collectors_ribbon_info", ribbon_info, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("gh_update", update_github, filters=is_admin))
    app.add_handler(CommandHandler("settings", settings_menu, filters=dev_mode & not_banned_filter))
    app.add_handler(CommandHandler("notif", notify_free_pack, filters=dev_mode & not_banned_filter))

    # обработчики текстовых сообщений (для кнопок)
    app.add_handler(MessageHandler(dev_mode & other_button_filter & not_banned_filter, other_menu))
    app.add_handler(MessageHandler(dev_mode & anon_trade_button_filter & not_banned_filter,
                                   anon_trade_main_menu))
    app.add_handler(MessageHandler(dev_mode & offers_button_filter & not_banned_filter,
                                   anon_trade_choose_menu))
    app.add_handler(MessageHandler(dev_mode & my_offers_button_filter & not_banned_filter,
                                   anon_trade_show_my_offers))
    app.add_handler(MessageHandler(dev_mode & menu_button_filter, menu))
    app.add_handler(MessageHandler(dev_mode & roll_menu_button_filter & not_banned_filter, roll_menu))
    app.add_handler(MessageHandler(dev_mode & roll_button_filter & not_banned_filter, packs_menu))
    app.add_handler(MessageHandler(dev_mode & collection_menu_button_filter & not_banned_filter,
                                   collection_menu))
    app.add_handler(MessageHandler(dev_mode & collection_list_button_filter & not_banned_filter,
                                   view_collection_list))
    app.add_handler(MessageHandler(dev_mode & show_card_button_filter & not_banned_filter, list_cards))
    app.add_handler(MessageHandler(dev_mode & packs_shop_button_filter & not_banned_filter, packs_shop_menu))
    app.add_handler(MessageHandler(dev_mode & shop_button_filter & not_banned_filter, shop_menu))
    app.add_handler(MessageHandler(dev_mode & all_cards_button_filter & not_banned_filter,
                                   collection_completeness))
    app.add_handler(MessageHandler(dev_mode & coinflip_menu_button_filter & not_banned_filter, coinflip_menu))
    app.add_handler(MessageHandler(dev_mode & market_offers_button_filter & not_banned_filter, market_offers_menu))
    app.add_handler(MessageHandler(dev_mode & market_my_offers_button_filter & not_banned_filter,
                                   market_show_my_offers_list))
    app.add_handler(MessageHandler(dev_mode & market_button_filter & not_banned_filter, market_menu_new))
    app.add_handler(MessageHandler(dev_mode & market_button_filter & not_banned_filter, market_menu_new))
    app.add_handler(MessageHandler(dev_mode & pitstop_button_filter & not_banned_filter, pitstop_menu))
    app.add_handler(MessageHandler(dev_mode & settings_button_filter & not_banned_filter, settings_menu))

    # обработчик беседы (для продажи)
    app.add_handler(conv_handler)
    app.add_handler(trade_conv_handler)
    app.add_handler(pitstop_conv_handler)
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
