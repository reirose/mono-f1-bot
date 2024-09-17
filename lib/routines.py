"""
Рутинные функции, не столь относящиеся к игровому процессу, сколь к работе бота
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from lib.classes.user import User
from lib.init import CARDS_COLLECTION, USER_COLLECTION, BOT_INFO
from lib.variables import cards_list, cards_dict, cards_by_category, roll_cards_dict

scheduler = BackgroundScheduler()


def update_free_roll():
    """
    Добавление крутки пользователям
    """
    resp = USER_COLLECTION.update_many({}, {"$inc": {"available_rolls": 1}})
    logging.log(BOT_INFO, f"Updated %i free rolls" % resp.matched_count)


def update_cards():
    """
    Обновление всех необходимых локальных списков и словарей с картами из БД
    """
    db_data = list(CARDS_COLLECTION.find({}, {"_id": 0}))
    for x in db_data:
        cards_list.append(x)
        cards_dict.update({x["code"]: x})
        cards_by_category[x["category"]].append(x["code"])
        if x["category"] not in ["limited"]:
            roll_cards_dict.update({x["code"]: x})

    logging.log(BOT_INFO, f"Updated {len(db_data)} cards.")


def restart_status_reset():
    resp = USER_COLLECTION.update_many({}, {"$set": {"status": "idle"}})
    logging.log(BOT_INFO, "Status reset successful (%i)" % resp.matched_count)


restart_status_reset()
