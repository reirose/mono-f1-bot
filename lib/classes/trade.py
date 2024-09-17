from collections import namedtuple

from pymongo.results import UpdateResult

from lib.init import TRADES_COLLECTION

TradeData = namedtuple("TradeData",
                       ['id', 'sender', 'receiver', 'sender_list', 'receiver_list', 'status'])


class Trade:
    def __init__(self, data):
        self.id = data["id"]
        self.sender = data["sender"]
        self.receiver = data["receiver"]
        self.sender_list = data["sender_list"]
        self.receiver_list = data["receiver_list"]
        self.status = data["status"]

    @staticmethod
    def exists(trade_id: int) -> bool:
        res = [x for x in TRADES_COLLECTION.find({"id": trade_id})]
        return True if res else False

    @staticmethod
    def get(trade_id: int):
        if not Trade.exists(trade_id):
            return None

        data = TRADES_COLLECTION.find_one({"id": trade_id}, {"_id": 0})
        return Trade(TradeData(**data))

    def write(self) -> bool:
        self.sender_list.sort()  # сортировка карт для более красивого отображения
        self.receiver_list.sort()  # сортировка карт для более красивого отображения
        res: UpdateResult = TRADES_COLLECTION.update_one({"id": self.id},
                                                         {"$set": {
                                                             "sender_list": self.sender_list,
                                                             "receiver_list": self.receiver_list
                                                         }},
                                                         upsert=False)

        return res.acknowledged
