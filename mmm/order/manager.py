import asyncio
import logging
from abc import ABCMeta, abstractmethod
from typing import Optional

from mmm.config import settings
from mmm.events.event import OrderEvent
from mmm.project_types import OrderResult
from mmm.schema import Storage
from mmm.schema.impl import default_storage


class OrderManager(metaclass=ABCMeta):
    @abstractmethod
    def create_order(self, order_event: "OrderEvent"): ...

    @abstractmethod
    def query_order(self, uniq_id): ...

    @abstractmethod
    async def query_order_async(self, uniq_id, timeout=8): ...


class DefaultOrderManager(OrderManager):
    def __init__(self, storage: "Storage" = default_storage):
        self.event_source = settings.EVENT_SOURCE_CONF.get(OrderEvent)
        if self.event_source is None:
            raise RuntimeError('can not find event source of OrderEvent.')
        self.storage = storage

    def create_order(self, order_event: "OrderEvent"):
        logging.info(f'create order, order_event :{order_event}')
        self.event_source.put_nowait(order_event)

    def query_order(self, uniq_id) -> Optional[OrderResult]:
        return self.storage.query_order(uniq_id)

    async def query_order_async(self, uniq_id, timeout=8):
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, self.query_order, uniq_id)
        return await asyncio.wait_for(future, timeout=timeout, loop=loop)