import logging

from copy import deepcopy
from typing import List

from mmm.core.hub.hub_factory import HubFactory
from mmm.core.hub.inner_event_hub.event import OrderCreationEvent
from mmm.core.storage import default_storage, Storage
from mmm.core.order.handler import OkexOrderHandler, OrderHandler, BinanceOrderHandler
from mmm.core.order.filter import Filter
from mmm.credential import Credential
from mmm.project_types import Exchange

logger = logging.getLogger(__name__)


class OrderExecutor:
    def __init__(self, storage: "Storage" = default_storage):
        self.order_event_hub = HubFactory().get_inner_event_hub()
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

    async def on_order_event(self, order_event: "OrderCreationEvent"):
        c = deepcopy(order_event)
        for middleware in self.middlewares:
            rv, reason = middleware.filter(c)
            if not rv:
                logger.error(f"order_event {order_event} is not permitted for the reason of {reason}")
                return
        order_handler = self.get_order_handler(order_event.exchange, order_event.credential)
        order_result = await order_handler.create_order(order_event)
        self.storage.save_order(order_result)

    async def run_executor(self):
        queue = self.order_event_hub.subscribe(OrderCreationEvent)
        while True:
            event = await queue.get()
            if event:
                await self.on_order_event(event)
