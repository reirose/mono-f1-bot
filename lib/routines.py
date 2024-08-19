import logging

from lib.init import CARDS_COLLECTION
from lib.variables import cards_list


def update_cards():
    db_data = list(CARDS_COLLECTION.find({}, {"_id": 0}))
    for x in db_data:
        cards_list.update({x["id"]: x["name"]})

    logging.log(logging.INFO, f"Updated {len(db_data)} cards.")
