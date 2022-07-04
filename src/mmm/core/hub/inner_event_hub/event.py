import pickle

from copy import deepcopy
from enum import Enum
from typing import Optional

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


class OrderCreationEvent(Event):
    def __init__(self, uniq_id: str, strategy_name: str, bot_id: str, exchange: "Exchange",
                 credential: "Credential", params: dict):
        super().__init__(clear(locals(), 'self'))
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
        super().__init__(clear(locals(), 'self'))
        self.bot_id = bot_id
        self.command = command


