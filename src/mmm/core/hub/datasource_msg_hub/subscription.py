from abc import ABCMeta, abstractmethod

from mmm.project_types import Exchange


class Subscription(metaclass=ABCMeta):

    @abstractmethod
    def get_exchange(self) -> "Exchange": ...

    @abstractmethod
    def equal_to(self, obj: "Subscription"): ...


class ResponseOfSub(metaclass=ABCMeta):
    """response of subscription."""

    def __init__(self, data=None):
        self._raw_data = data

    @abstractmethod
    def get_exchange(self) -> "Exchange": ...

    @abstractmethod
    def response_for(self, obj: "Subscription") -> bool: ...
