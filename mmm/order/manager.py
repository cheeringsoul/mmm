import logging

from mmm.events import default_event_source_conf, EventSource
from mmm.events.event import OrderEvent
from mmm.events import EventSourceConfig


class OrderManager:
    def __init__(self, event_source_conf: "EventSourceConfig" = default_event_source_conf):
        self.event_source: "EventSource" or None = event_source_conf.get(OrderEvent)
        if self.event_source is None:
            raise RuntimeError('OrderEvent事件源未配置！')

    def create_order(self, order_event: "OrderEvent"):
        logging.info(f'下单：订单类型{order_event.order_type}, 参数: {order_event.params}')
        self.event_source.put_nowait(order_event)

    def query_order(self, uniq_id):
        ''''''


default_order_manager = OrderManager()
