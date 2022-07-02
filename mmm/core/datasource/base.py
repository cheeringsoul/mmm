from abc import ABCMeta, abstractmethod
from typing import List

from mmm.core.hub.datasource_msg_hub.subscription import Subscription
from mmm.core.hub.hub_factory import HubFactory


class DataSource(metaclass=ABCMeta):

    def __init__(self):

        self.ds_msg_hub = HubFactory().get_ds_msg_hub()

    @abstractmethod
    async def subscribe(self, subscription: List["Subscription"]): ...
