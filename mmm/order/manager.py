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
        event_source_conf = settings.EVENT_SOURCE_CONF
        self.event_source: dict or None = event_source_conf.get(OrderEvent)
        if self.event_source is None:
            raise RuntimeError('OrderEvent事件源未配置！')

    def create_order(self, order_event: "OrderEvent"):
        logging.info(f'下单：订单类型{order_event.order_type}, 参数: {order_event.params}')
        self.event_source.put_nowait(order_event)

    def query_order(self, uniq_id):
        ''''''
