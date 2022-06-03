import asyncio
import logging
from abc import ABCMeta, abstractmethod
from sqlalchemy.orm import Session

from mmm.config import settings
from mmm.events.event import OrderEvent
from mmm.project_types import Order
from mmm.storage.sql.schema import engine, Order as OrderModel


class OrderManager(metaclass=ABCMeta):
    @abstractmethod
    def create_order(self, *args, **kwargs): ...

    @abstractmethod
    def query_order(self, *args, **kwargs): ...


class DefaultOrderManager(OrderManager):
    def __init__(self):
        self.event_source = settings.EVENT_SOURCE_CONF.get(OrderEvent)
        if self.event_source is None:
            raise RuntimeError('can not find event source of OrderEvent.')

    def create_order(self, order_event: "OrderEvent"):
        logging.info(f'create order, order type :{order_event.order_type}, params: {order_event.params}')
        self.event_source.put_nowait(order_event)

    def query_order(self, uniq_id, timeout=20) -> None or "Order":
        def do_query():
            with Session(engine) as session:
                while True:
                    rv = session.query(OrderModel).filter(uniq_id).first()
                    if rv is None:
                        asyncio.sleep(1)
                        continue
                    return Order(
                        exchange=rv.exchange,
                        order_id=rv.order_id,
                        client_order_id=rv.client_order_id,
                        instrument_id=rv.instrument_id,
                        currency=rv.currency,
                        order_type=rv.order_type,
                        side=rv.side,
                        avg_price=rv.avg_price,
                        turnover=rv.turnover,
                        volume=rv.volume
                    )
        loop = asyncio.get_running_loop()
        future = loop.run_in_executor(None, do_query)
        result = asyncio.wait_for(future, timeout, loop=loop)
        return result

