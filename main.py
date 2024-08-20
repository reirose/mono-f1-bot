import logging

from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler

from bin.menu import menu
from bin.roll import roll, roll_menu
from bin.service_commands import start
from bin.statistics import statistics
from lib.classes.user import User

from lib.init import TOKEN, client
from lib.filters import statistic_button_filter, menu_button_filter, roll_menu_button_filter, roll_button_filter
from lib.routines import update_cards, scheduler, update_free_roll

scheduler.start()

scheduler.add_job(update_cards, 'interval', hours=0.25)
scheduler.add_job(update_free_roll, 'cron', hour=20, minute=0, second=0)
scheduler.add_job(update_free_roll, 'cron', hour=8, minute=0, second=0)


def main():
    app: Application = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(statistic_button_filter, statistics))
    app.add_handler(MessageHandler(menu_button_filter, menu))
    app.add_handler(MessageHandler(roll_menu_button_filter, roll_menu))
    app.add_handler(MessageHandler(roll_button_filter, roll))

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    update_cards()
    logging.log(logging.INFO, "starting")
    main()
    client.close()
    logging.log(logging.INFO, "exiting")
