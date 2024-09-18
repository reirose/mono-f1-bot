import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, filters

from bin.callback_button_handler import button_callback
from bin.collection import view_collection_list, collection_menu, list_cards
from bin.market import market_menu, conv_handler, buy_command
from bin.menu import menu
from bin.roll import roll, roll_menu
from bin.service_commands import start, dev_mode_change, unstuck
from bin.other import other_menu
from bin.shop import shop_menu

from lib.init import TOKEN, client, BOT_INFO
from lib.filters import (other_button_filter, menu_button_filter, roll_menu_button_filter, roll_button_filter,
                         collection_menu_button_filter, show_card_button_filter, collection_list_button_filter,
                         dev_mode, shop_button_filter, me_button_filter, market_button_filter, is_admin)
from lib.routines import update_cards, scheduler, update_free_roll

# Запуск планировщика задач и добаление в него:
# - обновление локальной БД карт раз в 15 минут
# - добавление бесплатных круток в 8 и 20 часов
scheduler.start()

scheduler.add_job(update_cards, 'interval', hours=0.25)
scheduler.add_job(update_free_roll, 'cron', hour=20, minute=0, second=0)
scheduler.add_job(update_free_roll, 'cron', hour=8, minute=0, second=0)


def main():
    # объект всего приложения
    app: Application = Application.builder().token(TOKEN).build()

    # текстовые команды (через "/")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("dm", dev_mode_change))
    app.add_handler(CommandHandler("unstuck", unstuck))
    app.add_handler(CommandHandler("buy", buy_command, has_args=True))

    # обработчики текстовых сообщений (для кнопок)
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

    # обработчик беседы (для продажи)
    app.add_handler(conv_handler)
    # обработчик инлайн кнопок
    app.add_handler(CallbackQueryHandler(button_callback))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    update_cards()
    logging.log(BOT_INFO, "starting")
    main()
    client.close()
    logging.log(BOT_INFO, "exiting")
