import logging
from abc import ABCMeta, abstractmethod

from mmm.config import settings
from mmm.events.event import OrderEvent


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

    def query_order(self, uniq_id):
        """"""
