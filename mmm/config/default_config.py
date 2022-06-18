from asyncio import Queue

from mmm.core.events.event import BarEvent, OrderEvent, Event, TradesEvent, OrderBookEvent, ControlEvent
from mmm.core.events.event_source import AsyncioQueueEventSource


EVENT_SOURCE_CONF = {  # event source config
    Event: AsyncioQueueEventSource(Queue()),
    TradesEvent: AsyncioQueueEventSource(Queue()),
    OrderBookEvent: AsyncioQueueEventSource(Queue()),
    BarEvent: AsyncioQueueEventSource(Queue()),
    OrderEvent: AsyncioQueueEventSource(Queue()),
    ControlEvent: AsyncioQueueEventSource(Queue())
}

DATABASE = 'sqlite:///mmm.db'
