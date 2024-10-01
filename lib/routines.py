"""
Рутинные функции, не столь относящиеся к игровому процессу, сколь к работе бота
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

from lib.init import CARDS_COLLECTION, USER_COLLECTION, BOT_INFO
from lib.variables import cards_list, cards_dict, cards_by_category, roll_cards_dict, type_sort_keys

scheduler = BackgroundScheduler()


def update_free_roll():
    """
    Добавление крутки пользователям
    """
    resp = USER_COLLECTION.update_many({}, {"$inc": {"rolls_available": 1}})
    logging.log(BOT_INFO, f"Updated %i free rolls" % resp.matched_count)


def update_cards():
    """
    Обновление всех необходимых локальных списков и словарей с картами из БД
    """
    db_data = sorted(list(CARDS_COLLECTION.find({}, {"_id": 0})),
                     key=lambda y: (type_sort_keys[y['type']], y['name']))
    for x in db_data:
        cards_list.append(x)
        cards_dict.update({x["code"]: x})
        cards_by_category[x["category"]].append(x["code"])
        if x["type"] not in ["limited"]:
            roll_cards_dict.update({x["code"]: x})

    logging.log(BOT_INFO, f"Updated {len(db_data)} cards.")


def restart_status_reset():
    resp = USER_COLLECTION.update_many({}, {"$set": {"status": "idle"}})
    logging.log(BOT_INFO, "Status reset successful (%i)" % resp.matched_count)


async def notify_free_pack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = USER_COLLECTION.find({}, {"_id": 0})
    for user in users:
        try:
            context.bot.send_message(chat_id=user.get("id"),
                                     text="Получен бесплатный пак. Иди скорее открывай")
        except BadRequest:
            pass

restart_status_reset()
