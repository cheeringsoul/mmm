import asyncio
import functools
import inspect
import logging

from collections import ChainMap
from datetime import datetime
from enum import Enum
from typing import Callable, List

from mmm.config import settings
from mmm.core.events.event import BotControlEvent, Command
from mmm.core.events.event_source import EventSource
from mmm.core.storage import default_storage, Storage
from mmm.core.strategy.decorators import register_handler
from mmm.core.strategy.strategy import Strategy
from mmm.exceptions import HandlerRegisterError, EventSourceNotFoundError

logger = logging.getLogger(__name__)


class BotStatus(Enum):
    Created = 0
    Running = 1
    Stopped = 2


class Bot:
    def __init__(self, strategy: "Strategy"):
        self.bot_id = strategy.bot_id
        self.strategy = strategy
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
                raise EventSourceNotFoundError(f'can not find event source of {event_type}.')
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


class HandlerMetaclass(type):
    def __new__(cls, name, bases, kwargs):  # noqa
        command_registry = {}
        for method_name, method in kwargs.items():
            command = getattr(method, '__command__', None)
            if command is None:
                continue
            if command in command_registry:
                raise HandlerRegisterError(f'You can not sub {command} twice.')
            command_registry[command] = method
        kwargs['__command_registry__'] = command_registry
        return super().__new__(cls, name, bases, kwargs)


class BotControlEventHandler(metaclass=HandlerMetaclass):
    def __init__(self, bot_registry: "BotRegistry", storage=default_storage):
        self.bot_registry = bot_registry
        self.storage: "Storage" = storage
        self.bot_tasks = {}
        self.persistent_task = {}

    def handel(self, event: "BotControlEvent"):
        command = event.command
        method = getattr(self, '__command_registry__').get(command, None)
        if method is None:
            logger.error(f"can not find handler of command {command} in BotControlEventHandler")
            return
        return method(event)

    def _clear_bot_task(self, bot_id):
        self.storage.create_or_update_bot(bot_id, status=BotStatus.Stopped)
        del self.bot_tasks[bot_id]

    def _clear_persistent_task(self, bot_id):
        del self.persistent_task[bot_id]

    async def persistent_bot(self, bot: "Bot"):
        s = datetime.utcnow()
        self.storage.create_or_update_bot(bot.bot_id, strategy_name=bot.strategy.strategy_name,
                                          status=BotStatus.Created)
        while (datetime.utcnow() - s).seconds < 15:
            task = self.bot_tasks.get(bot.bot_id)
            if task:
                if not task.done():
                    self.storage.create_or_update_bot(bot.bot_id, strategy_name=bot.strategy.strategy_name,
                                                      status=BotStatus.Running)
                    return
            await asyncio.sleep(0.5)

    async def _start_bot(self, bot: "Bot"):
        bot_id = bot.bot_id
        if bot_id not in self.bot_tasks:
            t = asyncio.create_task(bot.gather_tasks())
            self.bot_tasks[bot_id] = t
            t.add_done_callback(functools.partial(self._clear_bot_task, bot_id))

            t = asyncio.create_task(self.persistent_bot(bot))
            self.persistent_task[bot.bot_id] = t
            t.add_done_callback(functools.partial(self._clear_persistent_task, bot_id))

    async def _stop_bot(self, bot_id):
        task = self.bot_tasks.get(bot_id)
        if task:
            task.cancel()
            del self.bot_tasks[bot_id]

    @register_handler(Command.START_ALL)
    async def start_all_bot(self, event: "BotControlEvent"):
        bots = self.bot_registry.get_all_bot()
        for bot in bots:
            await self._start_bot(bot)

    @register_handler(Command.START_BOT)
    async def start_bot(self, event: "BotControlEvent"):
        bot_id = event.bot_id
        bot = self.bot_registry.get_bot(bot_id)
        await self._start_bot(bot)

    @register_handler(Command.STOP_BOT)
    async def stop_bot(self, event: "BotControlEvent"):
        await self._stop_bot(event.bot_id)

    @register_handler(Command.STOP_ALL)
    async def stop_bot(self, event: "BotControlEvent"):
        for bot_id, task in self.bot_tasks.items():
            await self._stop_bot(bot_id)
