from abc import ABCMeta, abstractmethod

from mmm.events.event import OrderEvent


class Analyzer(metaclass=ABCMeta):

    @abstractmethod
    def analysis(self, *args, **kwargs) -> "OrderEvent": ...
