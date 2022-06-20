import asyncio
import logging
import time
from abc import ABCMeta, abstractmethod
from typing import Optional

from mmm.config import settings
from mmm.core.events.event import OrderEvent
from mmm.project_types import OrderResult
from mmm.core.schema import Storage
from mmm.core.schema.impl import default_storage


class OrderManager(metaclass=ABCMeta):
    @abstractmethod
    def create_order(self, order_event: "OrderEvent"): ...

    @abstractmethod
    def query_order(self, uniq_id): ...

    @abstractmethod
    async def query_order_async(self, uniq_id, timeout): ...


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

    async def query_order_async(self, uniq_id, timeout):
        def do_query(_uniq_id, e: "asyncio.Event"):
            while not e.is_set():
                rv = self.query_order(_uniq_id)
                if rv:
                    return rv
                time.sleep(0.01)

        event = asyncio.Event()
        fut = asyncio.to_thread(do_query, event)
        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        except (asyncio.TimeoutError, Exception):
            event.set()
