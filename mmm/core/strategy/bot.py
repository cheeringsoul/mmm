import asyncio
import functools
import inspect
import logging
from abc import ABCMeta, abstractmethod

from collections import ChainMap
from datetime import datetime
from enum import Enum
from typing import Callable, List

from mmm.core.hub.hub_factory import HubFactory
from mmm.core.hub.inner_event_hub.event import Command, BotControlEvent
from mmm.core.storage import default_storage, Storage
from mmm.core.strategy.decorators import register_handler
from mmm.core.strategy.strategy import Strategy
from mmm.exceptions import HandlerRegisterError


logger = logging.getLogger(__name__)


class BotStatus(Enum):
    Created = 0
    Running = 1
    Stopped = 2


class Bot:
    def __init__(self, strategy: "Strategy"):
        self.bot_id = strategy.bot_id
        self.strategy = strategy
        self.ds_msg_hub = HubFactory().get_ds_msg_hub()

    async def gather_tasks(self):
        tasks = self.create_timed_tasks() + self.create_event_consuming_tasks()
        await asyncio.gather(*tasks)

    def on_close(self):
        sub_registry = self.strategy.get_sub_registry()
        for sub in sub_registry.get_subscriptions():
            self.ds_msg_hub.unsubscribe(sub)

    def create_timed_tasks(self):
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
        tasks = []
        registry = self.strategy.get_timer_registry()
        for interval, method_name in registry.items():
            method = getattr(self.strategy, method_name)
            name = f'{self.strategy.strategy_name}.timer({interval})'
            tasks.append(asyncio.create_task(_timer(name, interval, method), name=f'task.timer.{interval}'))
        return tasks

    def create_event_consuming_tasks(self):
        async def consume(name_, queue_, callback):
            try:
                while True:
                    event = await queue_.get()
                    if inspect.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
            except asyncio.CancelledError as e:
                if str(e):
                    logger.error(f"task {name_} {e}")
                else:
                    logger.error(f"task {name_} canceled.")
        tasks = []
        sub_registry = self.strategy.get_sub_registry()
        for sub, method_name in sub_registry.items():
            queue = self.ds_msg_hub.subscribe(sub)
            method = getattr(self.strategy, method_name)
            name = f'task.{self.strategy.strategy_name}.sub.{sub.__class__.__name__}'
            tasks.append(asyncio.create_task(consume(name, queue, method), name=name))
        return tasks


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
        command_registry = cls.__get_command_registry__(cls, bases)
        for method_name, method in kwargs.items():
            command = getattr(method, '__command__', None)
            if command is None:
                continue
            if command in command_registry:
                raise HandlerRegisterError(f'You can not sub {command} twice.')
            command_registry[command] = method_name
        kwargs['__command_registry__'] = command_registry
        return super().__new__(cls, name, bases, kwargs)

    def __get_command_registry__(cls, bases):  # noqa
        if not bases:
            return {}
        for each in bases:
            if getattr(each, '__command_registry__'):
                command_registry = getattr(each, '__command_registry__')
                break
        else:
            command_registry = {}
        return command_registry


class HandlerABCMetaclass(ABCMeta, HandlerMetaclass):
    ...


class BotCommandHandler(metaclass=HandlerABCMetaclass):

    @abstractmethod
    async def start_bot(self, event: "BotControlEvent"): ...

    @abstractmethod
    async def stop_bot(self, event: "BotControlEvent"): ...

    @abstractmethod
    async def start_all_bot(self, event: "BotControlEvent"): ...

    @abstractmethod
    async def stop_all_bot(self, event: "BotControlEvent"): ...

    @register_handler(Command.START_BOT)
    async def __start_bot__(self, event: "BotControlEvent"):
        await self.start_bot(event)

    @register_handler(Command.STOP_BOT)
    async def __stop_bot__(self, event: "BotControlEvent"):
        await self.stop_bot(event)

    @register_handler(Command.START_ALL)
    async def __start_all_bot__(self, event: "BotControlEvent"):
        await self.start_all_bot(event)

    @register_handler(Command.STOP_ALL)
    async def __stop_all_bot__(self, event: "BotControlEvent"):
        await self.stop_all_bot(event)

    def handel(self, event: "BotControlEvent"):
        command = event.command
        method_name = getattr(self, '__command_registry__').get(command, None)
        if method_name is None:
            logger.error(f"can not find handler of command {command} in BotControlEventHandler")
            return
        return getattr(self, method_name)(event)


class BotControlEventHandler(BotCommandHandler):
    def __init__(self, bot_registry: "BotRegistry", storage=default_storage):
        super().__init__()
        self.bot_registry = bot_registry
        self.storage: "Storage" = storage
        self.bot_tasks = {}
        self.persistent_task = set()

    def _clear_bot_task(self, bot, task):
        bot.on_close()
        bot_id = bot.bot_id
        self.storage.create_or_update_bot(bot_id, status=BotStatus.Stopped.value)
        del self.bot_tasks[bot_id]

    async def persistent_bot(self, bot: "Bot"):
        s = datetime.utcnow()
        self.storage.create_or_update_bot(bot.bot_id, strategy_name=bot.strategy.strategy_name,
                                          status=BotStatus.Created.value)
        while (datetime.utcnow() - s).seconds < 15:
            task = self.bot_tasks.get(bot.bot_id)
            if task:
                if not task.done():
                    self.storage.create_or_update_bot(bot.bot_id, strategy_name=bot.strategy.strategy_name,
                                                      status=BotStatus.Running.value)
                    return
            await asyncio.sleep(0.5)

    def _start_bot(self, bot):
        bot_id = bot.bot_id
        if bot_id not in self.bot_tasks or self.bot_tasks[bot_id].done():
            t = asyncio.create_task(bot.gather_tasks())
            self.bot_tasks[bot_id] = t
            t.add_done_callback(functools.partial(self._clear_bot_task, bot))

            t = asyncio.create_task(self.persistent_bot(bot))
            self.persistent_task.add(t)
            t.add_done_callback(self.persistent_task.discard)

    async def start_all_bot(self, event: "BotControlEvent"):
        bots = self.bot_registry.get_all_bot()
        for bot in bots:
            self._start_bot(bot)

    async def start_bot(self, event: "BotControlEvent"):
        bot_id = event.bot_id
        bot = self.bot_registry.get_bot(bot_id)
        self._start_bot(bot)

    async def stop_bot(self, event: "BotControlEvent"):
        task = self.bot_tasks.get(event.bot_id)
        if task:
            task.cancel()

    async def stop_all_bot(self, event: "BotControlEvent"):
        for bot_id, task in self.bot_tasks.items():
            task.cancel()
