import logging

from apscheduler.schedulers.background import BackgroundScheduler

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes

from bin.roll import roll
from bin.service_commands import start
from bin.statistics import statistics

from lib.init import TOKEN, client
from lib.filters import statistic_button_filter
from lib.routines import update_cards

from lib.variables import cards_list


async def a(_: Update, __: ContextTypes.DEFAULT_TYPE):
    print(cards_list)


def main():
    scheduler = BackgroundScheduler()
    app: Application = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("roll", roll))
    app.add_handler(CommandHandler("a", a))
    app.add_handler(MessageHandler(statistic_button_filter, statistics))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

    scheduler.add_job(update_cards, 'interval', hours=0.25)


if __name__ == "__main__":
    update_cards()

    logging.log(logging.INFO, "starting")
    main()
    client.close()
    logging.log(logging.INFO, "exiting")
