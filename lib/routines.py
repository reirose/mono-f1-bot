import logging

from apscheduler.schedulers.background import BackgroundScheduler

from lib.classes.user import User
from lib.init import CARDS_COLLECTION, USER_COLLECTION
from lib.variables import cards_list

scheduler = BackgroundScheduler()


def update_free_roll():
    user_ids = [x["id"] for x in list(USER_COLLECTION.find({}, {"_id": 0}))]
    for user_id in user_ids:
        user = User.get(None, update=user_id)
        user.rolls_available += 1
        user.write()

        logging.log(logging.INFO, f"Updated free roll @ {user.id}")


def update_cards():
    db_data = list(CARDS_COLLECTION.find({}, {"_id": 0}))
    for x in db_data:
        cards_list.update({x["id"]: x["name"]})

    logging.log(logging.INFO, f"Updated {len(db_data)} cards.")
