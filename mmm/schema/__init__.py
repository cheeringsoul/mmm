from abc import ABCMeta, abstractmethod
from typing import Optional

from mmm.project_types import OrderResult


class Storage(metaclass=ABCMeta):

    @abstractmethod
    def save_order(self, order_result: "OrderResult"): ...

    @abstractmethod
    def query_order(self, uniq_id: str) -> Optional["OrderResult"]: ...
