import asyncio
import inspect
import logging
from collections import defaultdict

from mmm.config import settings
from mmm.credential import Credential
from mmm.core.events.event import Event, OrderEvent, ControlEvent
from mmm.core.events.event_source import EventSource
from mmm.core.order.manager import OrderManager, DefaultOrderManager
from mmm.project_types import Exchange

from typing import Type, Dict, Callable, List, Optional

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


class StrategyRunner:
    def __init__(self, strategies: List["Strategy"]):
        self.event_source_conf = settings.EVENT_SOURCE_CONF
        self.strategy_bot_conf = defaultdict(list)
        self.task_registry = StrategyTaskRegistry()
        for each in strategies:
            self.strategy_bot_conf[each.strategy_name].append(each.bot_id)
            if self.task_registry.exists(each.bot_id):
                raise RuntimeError(f'bot id {each.bot_id} repeated, you must use a globally unique id as bot id')
            self.task_registry.add_task(each.bot_id,
                                        self.create_schedule_task(each),
                                        self.create_event_consuming_tasks(each))

    def load_last_state(self):
        """load strategy state from database if exists"""
        # todo

    def start_bot(self, bot_id: str):
        """"""

    def start_strategy(self, bot_id: str):
        if not self.task_registry.exists(bot_id):
            logger.error(f'bot {bot_id} not fund.')
            return
        tasks = self.task_registry.get_tasks(bot_id)
        for each in tasks:
            if not each.done():
                logger.error(f'bot {bot_id} is already running')
                return
        asyncio.get_running_loop().create_task(gather_task(tasks))

    def start_all_strategy(self):
        bot_tasks = self.task_registry.get_all_tasks()

        async def _run():
            for _, tasks in bot_tasks.items():
                await gather_task(tasks)
        asyncio.get_running_loop().create_task(_run())

    def create_monitor(self):
        event_source = self.event_source_conf.get(ControlEvent)

        async def _monitor():
            while True:
                event: "ControlEvent" = await event_source.get()
                if event.command == 'stop':
                    self.stop_bot(event.bot_id)
                elif event.command == 'stopall':
                    self.stop_all()

        asyncio.get_running_loop().create_task(_monitor())

    def stop_bot(self, bot_id):
        tasks = self.task_registry.get_tasks(bot_id)
        if not tasks:
            return
        for task in tasks:
            task.cancel()

    def stop_all(self):
        """todo"""

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
