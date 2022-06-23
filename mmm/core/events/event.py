import pickle

from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, Optional

from mmm.credential import Credential
from mmm.project_types import Exchange


def clear(data, key):
    data = deepcopy(data)
    if key in data:
        del data[key]
    return data


class Event:
    def __init__(self, data=None):
        self._raw_data = data

    @property
    def raw_data(self):
        return self._raw_data

    def __repr__(self):
        return str(self._raw_data)

    @classmethod
    def decode(cls, data):
        return pickle.loads(data)

    def encode(self):
        return pickle.dumps(self)


class TradesEvent(Event):

    def __init__(self, inst_id: str, price: Decimal, volume: Decimal, side: str, ts: datetime, origin_data: Dict):
        super(TradesEvent, self).__init__(origin_data)
        self.inst_id: str = inst_id
        self.price: Decimal = price
        self.volume: Decimal = volume
        self.side: str = side
        self.ts: datetime = ts


class OrderBookEvent(Event):

    def __init__(self):
        super(OrderBookEvent, self).__init__()


class BarEvent(Event):

    def __init__(self, bar_type: str, inst_id: str, ts: datetime, open_price: Decimal, high_price: Decimal,
                 low_price: Decimal, close_price: Decimal, volume: Decimal, volume_ccy: Decimal, origin_data: Dict):
        """
        :param volume: 交易量，以张为单位, 如果是衍生品合约，数值为合约的张数。如果是币币/币币杠杆，数值为交易货币的数量。
        :param volume_ccy: 交易量，以币为单位 如果是衍生品合约，数值为交易货币的数量。如果是币币/币币杠杆，数值为计价货币的数量。
        """
        super(BarEvent, self).__init__(origin_data)
        self.bar_type: str = bar_type
        self.inst_id: str = inst_id
        self.ts: datetime = ts
        self.open_price: Decimal = open_price
        self.high_price: Decimal = high_price
        self.low_price: Decimal = low_price
        self.close_price: Decimal = close_price
        self.volume: Decimal = volume
        self.volume_ccy: Decimal = volume_ccy


class OrderEvent(Event):
    def __init__(self, uniq_id: str, strategy_name: str, bot_id: str, exchange: "Exchange",
                 credential: "Credential", params: dict):
        super(OrderEvent, self).__init__(clear(locals(), 'self'))
        self.uniq_id: str = uniq_id
        self.strategy_name: str = strategy_name
        self.bot_id: str = bot_id
        self.exchange: "Exchange" = exchange
        self.credential: "Credential" = credential
        self.params: dict = params


class Command(Enum):
    START_BOT = 1
    STOP_BOT = 2
    START_ALL = 3
    STOP_ALL = 4


class BotControlEvent(Event):

    def __init__(self, command: "Command", bot_id: Optional[str] = None):
        super(BotControlEvent, self).__init__(clear(locals(), 'self'))
        self.bot_id = bot_id
        self.command = command
