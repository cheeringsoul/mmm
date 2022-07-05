import asyncio
import logging
import time

from abc import ABCMeta, abstractmethod
from typing import Optional

from mmm.core.hub.hub_factory import HubFactory
from mmm.core.hub.inner_event_hub.event import OrderCreationEvent
from mmm.core.storage import default_storage, Storage
from mmm.project_types import OrderResult


class OrderManager(metaclass=ABCMeta):

    def __init__(self):
        self.msg_hub = HubFactory().get_inner_event_hub()

    @abstractmethod
    def create_order(self, order_event: "OrderCreationEvent"): ...

    @abstractmethod
    def query_order(self, uniq_id): ...

    @abstractmethod
    async def query_order_async(self, uniq_id, timeout): ...


class DefaultOrderManager(OrderManager):
    def __init__(self, storage: "Storage" = default_storage):
        super().__init__()
        self.storage = storage

    def create_order(self, order_event: "OrderCreationEvent"):
        logging.info(f'create order, order_event :{order_event}')
        self.msg_hub.publish(order_event)

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
        fut = asyncio.to_thread(do_query, uniq_id, event)
        try:
            return await asyncio.wait_for(fut, timeout=timeout)
        except (asyncio.TimeoutError, Exception):
            event.set()
