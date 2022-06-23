from asyncio import Queue

from mmm.core.events.event import BarEvent, OrderEvent, Event, TradesEvent, OrderBookEvent, BotControlEvent
from mmm.core.events.event_source import AsyncioQueueEventSource


EVENT_SOURCE_CONF = {  # event source config
    Event: AsyncioQueueEventSource(Queue()),
    TradesEvent: AsyncioQueueEventSource(Queue()),
    OrderBookEvent: AsyncioQueueEventSource(Queue()),
    BarEvent: AsyncioQueueEventSource(Queue()),
    OrderEvent: AsyncioQueueEventSource(Queue()),
    BotControlEvent: AsyncioQueueEventSource(Queue())
}

STRATEGIES = []

DATABASE = 'sqlite:///mmm.db'

STRATEGY_SERVER = {  # strategy server that receive control message
    'HOST': '0.0.0.0',
    'PORT': 6666,
}
