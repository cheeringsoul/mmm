import asyncio.queues
import logging
from mmm.config import settings
from mmm.events.event import Event


class Dispatcher:

    def __init__(self):
        self.event_source_conf = settings.EVENT_SOURCE_CONF

    async def dispatch(self, event: "Event"):
        event_source = self.event_source_conf.get(type(event))
        if event_source is None:
            raise RuntimeError(f'{event}找不到对应的事件源')
        try:
            event_source.put_nowait(event)
        except asyncio.queues.QueueFull:
            logging.error(event)


dispatcher = Dispatcher()
