from typing import List

from mmm.core.datasource.base import DataSource
from mmm.core.hub.datasource_msg_hub.subscription import Subscription


class BinanceWsDatasource(DataSource):

    async def subscribe(self, subscription: List["Subscription"]):
        """todo"""
