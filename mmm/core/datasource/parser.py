from abc import ABC, abstractmethod
from typing import List

from mmm.core.hub.datasource_msg_hub.subscription import ResponseOfSub


class Parser(ABC):
    @abstractmethod
    def parse(self, data) -> List["ResponseOfSub"]:
        """"""


class ParserFactory:
    def __init__(self):
        self.__registry__ = {}

    def get(self, channel: str) -> "Parser":
        for key in self.__registry__.keys():
            if channel.startswith(key):
                return self.__registry__[key]
        else:
            raise RuntimeError(f'can not find a message parser of {channel}')

    def register(self, channel: str, parser: "Parser"):
        self.__registry__[channel] = parser
