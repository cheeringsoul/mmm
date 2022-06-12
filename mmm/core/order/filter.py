from abc import ABCMeta, abstractmethod

from mmm.core.events.event import OrderEvent


class Filter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, order_event: "OrderEvent") -> bool: ...


class CoinFilter(Filter):
    def filter(self, order_event: "OrderEvent"):
        return True, ''
