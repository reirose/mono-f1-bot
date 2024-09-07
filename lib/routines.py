"""
Рутинные функции, не столь относящиеся к игровому процессу, сколь к работе бота
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler

from lib.classes.user import User
from lib.init import CARDS_COLLECTION, USER_COLLECTION
from lib.variables import cards_list, cards_dict, cards_by_category

scheduler = BackgroundScheduler()


def update_free_roll():
    """
    Добавление крутки пользователям
    """
    user_ids = [x["id"] for x in list(USER_COLLECTION.find({}, {"_id": 0}))]
    for user_id in user_ids:
        user = User.get(None, update=user_id)
        user.rolls_available += 1
        user.write()

        logging.log(logging.INFO, f"Updated free roll @ {user.id}")


def update_cards():
    """
    Обновление всех необходимых локальных списков и словарей с картами из БД
    """
    db_data = list(CARDS_COLLECTION.find({}, {"_id": 0}))
    for x in db_data:
        cards_list.append(x)
        cards_dict.update({x["code"]: x})
        cards_by_category[x["category"]].append(x["code"])

    logging.log(logging.INFO, f"Updated {len(db_data)} cards.")
