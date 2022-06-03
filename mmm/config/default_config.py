from asyncio import Queue

from mmm.events.event import BarEvent, OrderEvent, Event, TradesEvent, OrderBookEvent
from mmm.events.event_source import AsyncioQueueEventSource
from mmm.order.manager import DefaultOrderManager


ORDER_MANAGER = DefaultOrderManager()   # default order manager

EVENT_SOURCE_CONF = {  # event source config
    Event: AsyncioQueueEventSource(Queue()),
    TradesEvent: AsyncioQueueEventSource(Queue()),
    OrderBookEvent: AsyncioQueueEventSource(Queue()),
    BarEvent: AsyncioQueueEventSource(Queue()),
    OrderEvent: AsyncioQueueEventSource(Queue())
}

DATABASE = {
    'db_type': 'sqlite',
    'uri': 'mmm.db'
}
