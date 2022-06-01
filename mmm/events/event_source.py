from abc import ABC, abstractmethod
from asyncio import Queue
from typing import Type, Dict

from frozendict import frozendict

from .event import TradesEvent, OrderBookEvent, Event, OrderEvent, BarEvent


class EventSource(ABC):

    @abstractmethod
    def put_nowait(self, event: "Event"):
        """"""

    @abstractmethod
    async def get(self) -> "Event":
        """"""


class AsyncioQueueEventSource(EventSource):

    def __init__(self, queue: Queue):
        self.queue = queue

    def put_nowait(self, event: "Event"):
        self.queue.put_nowait(event)

    async def get(self) -> "Event":
        rv = await self.queue.get()
        self.queue.task_done()
        return rv


# class EventSourceConfig:
#     def __init__(self, kwargs: Dict[Type[Event], EventSource]):
#         self._config: Dict[Type[Event], EventSource] = frozendict(kwargs)
#
#     def get(self, event: Type[Event]) -> EventSource or None:
#         return self._config.get(event, None)


# default_queue_length = 10000
# default_event_source_conf = EventSourceConfig({
#     Event: AsyncioQueueEventSource(Queue(default_queue_length)),
#     TradesEvent: AsyncioQueueEventSource(Queue(default_queue_length)),
#     OrderBookEvent: AsyncioQueueEventSource(Queue(default_queue_length)),
#     BarEvent: AsyncioQueueEventSource(Queue(default_queue_length)),
#     OrderEvent: AsyncioQueueEventSource(Queue(default_queue_length))
# })
