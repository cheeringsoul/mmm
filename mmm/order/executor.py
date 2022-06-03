import asyncio
import logging

from mmm.config import settings
from mmm.credential import Credential
from mmm.events.event import OrderEvent
from mmm.order.handler import OkexOrderHandler, OrderHandler, BinanceOrderHandler
from mmm.project_types import Exchange


class OrderExecutor:
    def __init__(self):
        self.event_source = settings.EVENT_SOURCE_CONF.get(OrderEvent)
        if self.event_source is None:
            logging.error('can not find a event source of OrderEvent.')
        self.cached_executor = {}

    def get_order_executor(self, exchange: "Exchange", credential: "Credential"):
        executor = self.cached_executor.get(exchange, None)
        if executor is None:
            if exchange == Exchange.OKEX:
                executor = OkexOrderHandler(credential)
            elif exchange == Exchange.BINANCE:
                executor = BinanceOrderHandler(credential)
        self.set_executor(exchange, executor)
        return executor

    def set_executor(self, exchange: "Exchange", executor: "OrderHandler"):
        self.cached_executor[exchange] = executor

    async def on_order_event(self, order_event: "OrderEvent"):
        order_executor = self.get_order_executor(order_event.exchange, order_event.credential)
        loop = asyncio.get_running_loop()
        client_order_id = await loop.run_in_executor(None, lambda: order_executor.create_order(order_event))
        result = await loop.run_in_executor(None, lambda: order_executor.query_order(client_order_id, 5))
        if result is False:
            logging.error(f"订单{client_order_id}未查询到, 下单失败")
        else:
            logging.info(f"订单{client_order_id}执行成功")

    def create_task(self):

        async def _create_task():
            while True:
                event = await self.event_source.get()
                await self.on_order_event(event)

        asyncio.get_event_loop().create_task(_create_task(), name=f'order-executor-wait-for-orderevent-task')  # noqa
