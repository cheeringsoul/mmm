from abc import ABCMeta, abstractmethod


class MiddleWare(metaclass=ABCMeta):
    @abstractmethod
    def check(self, order_event: "OrderEvent") -> bool: ...


class CoinFilter(MiddleWare):
    def check(self, order_event: "OrderEvent") -> bool:
        return True
