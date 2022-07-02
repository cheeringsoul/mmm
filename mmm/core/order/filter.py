from abc import ABCMeta, abstractmethod

from mmm.core.hub.inner_event_hub.event import OrderCreationEvent


class Filter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, order_event: "OrderCreationEvent") -> bool: ...


class CoinFilter(Filter):
    def filter(self, order_event: "OrderCreationEvent"):
        return True, ''
