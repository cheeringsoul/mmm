import asyncio
import inspect
import logging
from collections import defaultdict

from mmm.config import settings
from mmm.credential import Credential
from mmm.core.events.event import Event, OrderEvent, StrategyControlEvent, Command
from mmm.core.events.event_source import EventSource
from mmm.core.order.manager import OrderManager, DefaultOrderManager
from mmm.project_types import Exchange

from typing import Type, Dict, Callable, List

logger = logging.getLogger(__name__)


class StrategyMeta(type):
    def __new__(cls, name, bases, kwargs):  # noqa
        event_registry = {}
        timer_registry = {}
        for method_name, method in kwargs.items():
            e = getattr(method, '__sub_event__', None)
            if e in event_registry.keys():
                raise RuntimeError(f"You can not sub {e.__name__} twice with different handler.")
            if e is not None:
                event_registry[e] = method_name
            interval = getattr(method, '__timer_interval__', None)
            if interval is not None:
                timer_registry[interval] = method_name

        kwargs['__event_registry__'] = event_registry
        kwargs['__timer_registry__'] = timer_registry
        return super().__new__(cls, name, bases, kwargs)


class Strategy(metaclass=StrategyMeta):
    __event_registry__: Dict[Type[Event], str] = {}
    __timer_registry__: Dict[int, str] = {}

    def __init__(self, bot_id: str, credential: "Credential", order_manager=None):
        self.bot_id = bot_id  # a unique id represent for the strategy bot
        self.credential = credential
        self.order_manager: OrderManager = order_manager or DefaultOrderManager()

    @classmethod
    def get_strategy_name(cls):
        return f"{cls.__module__}.{cls.__name__}"

    @property
    def strategy_name(self):
        return self.get_strategy_name()

    def create_order(self, uniq_id: str, exchange: "Exchange", params):
        """
        :param uniq_id: an unique id represent for this request
        :param exchange: such as okex, binance
        :param params: params that exchange api required
        :return:
        """
        uniq_id, self.get_strategy_name(), self.bot_id, exchange, self.credential, params
        event = OrderEvent(
            uniq_id=uniq_id,
            strategy_name=self.get_strategy_name(),
            bot_id=self.bot_id,
            exchange=exchange,
            credential=self.credential,
            params=params
        )
        self.order_manager.create_order(event)

    def create_batch_order(self):
        ...

    def __repr__(self):
        return f'strategy.{self.get_strategy_name()}'


async def gather_task(tasks):
    try:
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
        for task in done:
            name = task.get_name()
            logger.info(f"task {name} done!")
        for task in pending:
            task.cancel()
    except Exception as e:
        logger.exception(e)


class StrategyTaskRegistry:
    def __init__(self):
        self._data = defaultdict(dict)

    def add_task(self, bot_id: str, schedule_task, event_consuming_task):
        logger.warning(f"bot id {bot_id} already exists in registry, the original value will be overwritten.")
        self._data[bot_id] = {
            'schedule_task': schedule_task,
            'event_consuming_task': event_consuming_task
        }

    def exists(self, bot_id: str):
        return bot_id in self._data

    def get_tasks(self, bot_id: str, task_type: str = 'all'):
        if task_type == 'all':
            schedule_task = self._data[bot_id].get('schedule_task', [])
            event_consuming_task = self._data[bot_id].get('event_consuming_task', [])
            return schedule_task + event_consuming_task
        else:
            return self._data[bot_id].get(task_type)

    def get_all_tasks(self):
        return {bot_id: self.get_tasks(bot_id) for bot_id in self._data}


class StrategyControlEventHandler:
    def __init__(self, task_registry: "StrategyTaskRegistry"):
        self.task_registry = task_registry
        self.handler_conf = {
            Command.START_BOT: self.stop_bot,
            Command.STOP_BOT: self.stop_bot,
            Command.START_ALL: self.start_all_bot,
            Command.STOP_ALL: self.stop_all_bot
        }

    def handle(self, event: "StrategyControlEvent"):
        command = event.command
        handler = self.handler_conf.get(command)
        if handler is None:
            logger.warning(f'command {command} unregistered')
            return
        return handler(event)

    def save_bot(self, event: "StrategyControlEvent"):
        """todo"""

    def reload_bot(self, event: "StrategyControlEvent"):
        """todo"""

    def stop_bot(self, event: "StrategyControlEvent"):
        tasks = self.task_registry.get_tasks(event.bot_id)
        if not tasks:
            return
        for task in tasks:
            if not task.done():
                task.cancel()

    def stop_all_bot(self, event: "StrategyControlEvent"):
        tasks = self.task_registry.get_all_tasks()
        for task in tasks.values():
            if not task.done():
                task.cancel()

    def start_bot(self, event: "StrategyControlEvent"):
        if not self.task_registry.exists(event.bot_id):
            logger.error(f'bot {event.bot_id} not fund.')
            return
        tasks = self.task_registry.get_tasks(event.bot_id)
        for each in tasks:
            if not each.done():
                logger.error(f'bot {event.bot_id} is already running')
                return
        asyncio.get_running_loop().create_task(gather_task(tasks))

    def start_all_bot(self, event: "StrategyControlEvent"):
        bot_tasks = self.task_registry.get_all_tasks()

        async def _run():
            for _, tasks in bot_tasks.items():
                await gather_task(tasks)
        asyncio.get_running_loop().create_task(_run())


class StrategyRunner:
    def __init__(self, strategies: List["Strategy"]):
        self.event_source_conf = settings.EVENT_SOURCE_CONF
        self.task_registry = StrategyTaskRegistry()
        for each in strategies:
            if self.task_registry.exists(each.bot_id):
                raise RuntimeError(f'bot id {each.bot_id} repeated, you must use a globally unique id as bot id')
            self.task_registry.add_task(each.bot_id, self.create_schedule_task(each),
                                        self.create_event_consuming_tasks(each))
        self.control_event_handler = StrategyControlEventHandler(self.task_registry)

    def run(self):
        event_source = self.event_source_conf.get(StrategyControlEvent)

        async def _run():
            while True:
                event: "StrategyControlEvent" = await event_source.get()
                self.control_event_handler.handle(event)

        asyncio.get_running_loop().create_task(_run())

    def run_all_strategy(self):
        self.run()
        event_source = self.event_source_conf.get(StrategyControlEvent)
        event = StrategyControlEvent(Command.START_ALL)
        event_source.put_nowait(event)

    def create_schedule_task(self, strategy):  # noqa
        async def _timer(i: int, callback: Callable, name: str):
            try:
                callback()
                while True:
                    await asyncio.sleep(i)
                    if inspect.iscoroutinefunction(callback):
                        await callback()
                    else:
                        callback()
            except asyncio.CancelledError:
                logger.error(f"task {name} canceled.")
        tasks = []
        registry = strategy.__timer_registry__
        for interval, method_name in registry.items():
            method = getattr(strategy, method_name)
            task_name = f'task.{strategy}.timer({interval}'
            t = asyncio.create_task(_timer(interval, method, task_name), name=task_name)
            tasks.append(t)
        return tasks

    def create_event_consuming_tasks(self, strategy):
        async def _create_task(e: "EventSource", c: Callable, name: str):
            try:
                while True:
                    event = await e.get()
                    if inspect.iscoroutinefunction(c):
                        await c(event)
                    else:
                        c(event)
            except asyncio.CancelledError:
                logger.error(f"task {name} canceled.")

        tasks = []
        registry = strategy.__event_registry__
        for event_type, method_name in registry.items():
            event_source = self.event_source_conf.get(event_type)
            if event_source is None:
                logger.error(f'can not find event source of {event_type}.')
            method = getattr(strategy, method_name)
            task_name = f'task.{strategy}.wait.{event_type}'
            t = asyncio.create_task(_create_task(event_source, method, task_name), name=task_name)
            tasks.append(t)
        return tasks
