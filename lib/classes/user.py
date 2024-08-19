import logging
from collections import namedtuple

from pymongo.results import UpdateResult
from telegram import User as TelegramUser

from lib.init import USER_COLLECTION

UserData = namedtuple("UserData",
                      ['id', 'username', 'collection', 'last_roll', 'rolls_available'])


class User:
    def __init__(self, data: UserData):
        self.id: str = data.id
        self.username: str = data.username
        self.collection: list = data.collection
        self.last_roll: int = data.last_roll
        self.rolls_available: int = data.rolls_available

    @staticmethod
    def user_registered(telegram_id: int) -> bool:
        res = [x for x in USER_COLLECTION.find({"id": telegram_id})]
        return True if res else False

    @staticmethod
    def register(user: TelegramUser) -> None:
        user_data = {"id": user.id,
                     "username": user.username,
                     "collection": [],
                     "last_roll": 0,
                     "rolls_available": 1}
        USER_COLLECTION.insert_one(user_data)
        logging.log(logging.INFO, "Registered user %s" % user.username)

    @staticmethod
    def get(user: TelegramUser):
        if not User.user_registered(user.id):
            User.register(user)

        data = USER_COLLECTION.find_one({"id": user.id}, {"_id": 0})
        return User(UserData(**data))

    def write(self) -> bool:
        res: UpdateResult = USER_COLLECTION.update_one({"id": self.id},
                                                       {"$set": {
                                                           "username": self.username,
                                                           "collection": self.collection,
                                                           "last_roll": self.last_roll,
                                                           "rolls_available": self.rolls_available
                                                       }},
                                                       upsert=False)
        return res.acknowledged
