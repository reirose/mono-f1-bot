import datetime
import logging
import time
from collections import namedtuple
from typing import Union

from pymongo.results import UpdateResult
from telegram import User as TelegramUser

from lib.init import USER_COLLECTION

# кастомный тип переменной для более быстрой обработки инфы с БД
UserData = namedtuple("UserData",
                      ['id', 'username', 'dor', 'collection', 'last_roll', 'rolls_available', 'status',
                       'coins', 'market'])


class User:
    def __init__(self, data: UserData):
        self.id: str = data.id
        self.username: str = data.username
        self.collection: list = data.collection
        self.last_roll: int = data.last_roll
        self.rolls_available: int = data.rolls_available
        self.date_of_registration: int = data.dor
        self.status: str = data.status
        self.coins: int = data.coins
        self.market: str = data.market

    @staticmethod
    def user_registered(telegram_id: int) -> bool:
        """
        Проверка есть ли пользователь в БД
        :param telegram_id: численный id пользователя в тг (напр. 352318827)
        :return: true, если зарегистрирован
        """
        res = [x for x in USER_COLLECTION.find({"id": telegram_id})]
        return True if res else False

    @staticmethod
    def register(user: TelegramUser) -> None:
        """
        Регистрация пользователя
        :param user: объект пользователя тг (не id, не username, именно весь пакет данных) (да, много памяти занимает,
        но это единоразовая процедура для каждого пользователя)
        """
        user_data = {"id": user.id,
                     "username": user.username,
                     "collection": [],
                     "last_roll": time.time(),
                     "rolls_available": 1,
                     "dor": datetime.datetime.now().timestamp(),
                     "status": "idle",
                     "coins": 0,
                     "market": ""}
        USER_COLLECTION.insert_one(user_data)
        logging.log(logging.INFO, "Registered user %s" % user.username)

    @staticmethod
    def get(user: Union[TelegramUser, None], update: Union[int, str] = None):
        """
        Формирование объекта пользователя из БД
        :param user: объект пользователя
        :param update: не помню, зачем делал, но можно не по объекту получить, а по id или username опльзователя
        :return:
        """
        if update:
            data = USER_COLLECTION.find_one({"id" if type(update) == int else "username": update}, {"_id": 0})
            return User(UserData(**data))

        if not User.user_registered(user.id):
            User.register(user)

        data = USER_COLLECTION.find_one({"id": user.id}, {"_id": 0})
        return User(UserData(**data))

    def write(self) -> bool:
        """
        Запись пользователя в БД
        :return: true, если всё ок
        """
        self.collection.sort()  # сортировка карт для более красивого отображения
        res: UpdateResult = USER_COLLECTION.update_one({"id": self.id},
                                                       {"$set": {
                                                           "username": self.username,
                                                           "collection": self.collection,
                                                           "last_roll": self.last_roll,
                                                           "rolls_available": self.rolls_available,
                                                           "status": self.status,
                                                           "coins": self.coins,
                                                           "market": self.market
                                                       }},
                                                       upsert=False)
        return res.acknowledged
