import time
from abc import ABC, abstractmethod


class OrderIDGenerator(ABC):
    @abstractmethod
    def gen(self): ...


class OkexOrderIDGenerator(OrderIDGenerator):
    """字母（区分大小写）与数字的组合，可以是纯字母、纯数字且长度要在1-32位之间。"""

    def gen(self):
        return int(time.time()*10**6)


class BinanceOrderIDGenerator(OrderIDGenerator):
    def gen(self):
        pass
