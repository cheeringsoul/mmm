import asyncio
import inspect
import logging

from mmm.config import settings
from mmm.credential import Credential
from mmm.core.events.event import Event, OrderEvent
from mmm.core.events.event_source import EventSource
from mmm.core.order.manager import OrderManager, DefaultOrderManager

from typing import Type, Dict, Callable

from mmm.project_types import Exchange


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


class StrategyRunner:
    def __init__(self, strategy: "Strategy"):
        self.strategy = strategy
        self.event_source_conf = settings.EVENT_SOURCE_CONF

    def load_last_state(self):
        """load strategy state from database if exists"""
        # todo

    def save_state(self):
        """save strategy state"""
        # todo

    def create_schedule_task(self):
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
        registry = self.strategy.__timer_registry__
        for interval, method_name in registry.items():
            method = getattr(self.strategy, method_name)
            task_name = f'task.{self.strategy}.timer({interval}'
            t = asyncio.create_task(_timer(interval, method, task_name), name=task_name)
            tasks.append(t)
        return tasks

    def create_listening_tasks(self):
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
        registry = self.strategy.__event_registry__
        for event_type, method_name in registry.items():
            event_source = self.event_source_conf.get(event_type)
            if event_source is None:
                logger.error(f'can not find event source of {event_type}.')
            method = getattr(self.strategy, method_name)
            task_name = f'task.{self.strategy}.wait.{event_type}'
            t = asyncio.create_task(_create_task(event_source, method, task_name), name=task_name)
            tasks.append(t)
        return tasks

    def create_tasks(self):
        tasks = self.create_listening_tasks()
        tasks.extend(self.create_schedule_task())
        try:
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)
            for task in done:
                name = task.get_name()
                logger.error(f"task {name} existed, with exception: {task.exception()}")
            for task in pending:
                task.cancel()
        except Exception as e:
            logger.exception(e)

