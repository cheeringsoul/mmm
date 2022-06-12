from abc import ABCMeta, abstractmethod

from mmm.core.strategy.signals import StrategySignal


class Analyzer(metaclass=ABCMeta):

    @abstractmethod
    def analysis(self, *args, **kwargs) -> "StrategySignal": ...
