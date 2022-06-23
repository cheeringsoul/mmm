import asyncio
import inspect
import logging

from collections import ChainMap
from enum import Enum
from typing import Callable, List

from mmm.config import settings
from mmm.core.events.event_source import EventSource
from mmm.core.strategy.strategy import Strategy


logger = logging.getLogger(__name__)


class BotStatus(Enum):
    Created = 0
    Running = 1
    Stopped = 2


class Bot:
    def __init__(self, strategy: "Strategy"):
        self.bot_id = strategy.bot_id
        self.strategy = strategy
        self.status = BotStatus.Created
        self.event_source_conf = settings.EVENT_SOURCE_CONF

    async def gather_tasks(self):
        tasks = []
        for name, job in ChainMap(self.create_timed_jobs(), self.create_event_consuming_jobs()).items():
            tasks.append(asyncio.create_task(job, name=name))
        await asyncio.gather(*tasks)

    def create_timed_jobs(self):
        async def _timer(name_: str, i: int, callback: Callable):
            try:
                callback()
                while True:
                    await asyncio.sleep(i)
                    if inspect.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
            except asyncio.CancelledError as e:
                if str(e):
                    logger.error(f"task {name_} {e}")
                else:
                    logger.error(f"task {name_} canceled.")
        job = {}
        registry = self.strategy.__timer_registry__
        for interval, method_name in registry.items():
            method = getattr(self.strategy, method_name)
            name = f'{self.strategy.strategy_name}.timer({interval})'
            job[name] = _timer(name, interval, method)
        return job

    def create_event_consuming_jobs(self):
        async def consume(name_: str, e: "EventSource", c: Callable):
            try:
                while True:
                    event = await e.get()
                    if inspect.iscoroutinefunction(c):
                        await c(event)
                    else:
                        c(event)
            except asyncio.CancelledError as e:
                if str(e):
                    logger.error(f"task {name_} {e}")
                else:
                    logger.error(f"task {name_} canceled.")
        jobs = {}
        registry = self.strategy.__event_registry__
        for event_type, method_name in registry.items():
            event_source = self.event_source_conf.get(event_type)
            if event_source is None:
                logger.error(f'can not find event source of {event_type}.')
            method = getattr(self.strategy, method_name)
            name = f'task.{self.strategy.strategy_name}.wait.{event_type}'
            jobs[name] = consume(name, event_source, method)
        return jobs


class BotRegistry:
    def __init__(self, bots: List["Bot"]):
        self._registry = {}
        for bot in bots:
            self.add_bot(bot)

    def add_bot(self, bot: "Bot"):
        self._registry[bot.bot_id] = bot

    def get_bot(self, bot_id: str) -> "Bot":
        return self._registry.get(bot_id)

    def get_all_bot(self):
        return self._registry.values()

    def exists(self, bot_id: str):
        return bot_id in self._registry
