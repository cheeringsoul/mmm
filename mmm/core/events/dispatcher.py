import asyncio.queues
import logging
from mmm.config import settings
from mmm.core.events.event import Event


logger = logging.getLogger(__name__)


class Dispatcher:

    def __init__(self):
        self.event_source_conf = settings.EVENT_SOURCE_CONF

    async def dispatch(self, event: "Event"):
        event_source = self.event_source_conf.get(type(event))
        if event_source is None:
            raise RuntimeError(f'can not find event source of type {event}')
        try:
            event_source.put_nowait(event)
        except asyncio.queues.QueueFull:
            logger.error(event)
