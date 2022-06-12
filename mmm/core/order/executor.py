import asyncio
import logging

from copy import deepcopy
from typing import List

from mmm.config import settings
from mmm.credential import Credential
from mmm.core.events.event import OrderEvent
from mmm.core.order.handler import OkexOrderHandler, OrderHandler, BinanceOrderHandler
from mmm.core.order.filter import Filter
from mmm.project_types import Exchange
from mmm.core.schema.impl import Storage, default_storage

logger = logging.getLogger(__name__)


class OrderExecutor:
    def __init__(self, storage: "Storage" = default_storage):
        self.event_source = settings.EVENT_SOURCE_CONF.get(OrderEvent)
        if self.event_source is None:
            logger.error('can not find a event source of OrderEvent.')
        self.storage: "Storage" = storage
        self.cached_handler = {}
        self.middlewares: List["Filter"] = []  # todo

    def get_order_handler(self, exchange: "Exchange", credential: "Credential"):
        executor = self.cached_handler.get(exchange, None)
        if executor is None:
            if exchange == Exchange.OKEX:
                executor = OkexOrderHandler(credential)
            elif exchange == Exchange.BINANCE:
                executor = BinanceOrderHandler(credential)
        self.set_handler(exchange, executor)
        return executor

    def set_handler(self, exchange: "Exchange", handler: "OrderHandler"):
        self.cached_handler[exchange] = handler

    async def on_order_event(self, order_event: "OrderEvent"):
        c = deepcopy(order_event)
        for middleware in self.middlewares:
            rv, reason = middleware.filter(c)
            if not rv:
                logger.error(f"order_event {order_event} is not permitted for the reason of {reason}")
                return
        order_handler = self.get_order_handler(order_event.exchange, order_event.credential)
        order_result = await order_handler.create_order(order_event)
        self.storage.save_order(order_result)

    def create_task(self):

        async def _create_task():
            while True:
                event = await self.event_source.get()
                await self.on_order_event(event)

        asyncio.get_event_loop().create_task(_create_task(), name=f'task.order.executor')
