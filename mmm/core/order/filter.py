from abc import ABCMeta, abstractmethod

from mmm.core.msg_hub.inner_msg_hub.event import OrderEvent


class Filter(metaclass=ABCMeta):
    @abstractmethod
    def filter(self, order_event: "OrderEvent") -> bool: ...


class CoinFilter(Filter):
    def filter(self, order_event: "OrderEvent"):
        return True, ''
