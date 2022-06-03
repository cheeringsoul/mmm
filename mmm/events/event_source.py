from abc import ABC, abstractmethod
from asyncio import Queue

from mmm.events.event import Event


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
