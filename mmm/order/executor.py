import asyncio
import logging

from copy import deepcopy
from typing import List

from sqlalchemy.orm import Session

from mmm.config import settings
from mmm.credential import Credential
from mmm.events.event import OrderEvent
from mmm.order.handler import OkexOrderHandler, OrderHandler, BinanceOrderHandler
from mmm.order.middleware import MiddleWare
from mmm.project_types import Exchange, Order
from mmm.storage.sql.schema import engine, Order as OrderModel


class OrderExecutor:
    def __init__(self):
        self.event_source = settings.EVENT_SOURCE_CONF.get(OrderEvent)
        if self.event_source is None:
            logging.error('can not find a event source of OrderEvent.')
        self.cached_handler = {}
        self.middlewares: List["MiddleWare"] = []

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

    def save(self, uniq_id: str, order: "Order"):
        order_model = OrderModel(uniq_id=uniq_id,
                                 exchange=order.exchange.name,
                                 order_id=order.order_id,
                                 client_order_id=order.client_order_id,
                                 instrument_id=order.instrument_id,
                                 currency=order.currency,
                                 order_type=order.order_type,
                                 side=order.side,
                                 avg_price=order.avg_price,
                                 turnover=order.turnover,
                                 volume=order.volume)
        with Session(engine) as session:
            session.add(order_model)
            session.commit()

    async def on_order_event(self, order_event: "OrderEvent"):
        c = deepcopy(order_event)
        for middleware in self.middlewares:
            rv, reason = middleware.check(c)
            if not rv:
                logging.error(f"order_event {order_event} is not permitted for the reason of {reason}")
                return

        order_handler = self.get_order_handler(order_event.exchange, order_event.credential)
        loop = asyncio.get_running_loop()
        client_order_id = await loop.run_in_executor(None, lambda: order_handler.create_order(order_event))
        rv = await loop.run_in_executor(None, lambda: order_handler.query_order(client_order_id, 5))
        if rv is None:
            logging.error(f"order {client_order_id} can not be found, please check it manually.")
        else:
            logging.info(f"order {client_order_id} success.")
            self.save(order_event.uniq_id, rv)

    def create_task(self):

        async def _create_task():
            while True:
                event = await self.event_source.get()
                await self.on_order_event(event)

        asyncio.get_event_loop().create_task(_create_task(), name=f'task.order.executor')
