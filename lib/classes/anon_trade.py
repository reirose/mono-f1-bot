from collections import namedtuple

TradeData = namedtuple("TradeData",
                       ["wts", "wtb"])


class AnonTrade:
    def __init__(self, trade_data: TradeData):
        self.wts = trade_data.wts
        self.wtb = trade_data.wtb
