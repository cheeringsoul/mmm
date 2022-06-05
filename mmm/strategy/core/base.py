import asyncio
import inspect
import logging

from mmm.config import settings
from mmm.credential import Credential
from mmm.events.event import Event
from mmm.events.event_source import EventSource
from mmm.order.manager import OrderManager, DefaultOrderManager

from typing import Type, Dict, Callable


class StrategyMeta(type):
    def __new__(cls, name, bases, kwargs):  # noqa
        event_registry = {}
        timer_registry = {}
        for method_name, method in kwargs.items():
            e = getattr(method, '__sub_event__', None)
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

    def __init__(self, uniq_id: str, credential: "Credential", order_manager=None):
        self._strategy_id = uniq_id  # a unique id represent for the strategy instance
        self.credential = credential
        self.order_manager: OrderManager = order_manager or DefaultOrderManager()

    def get_id(self) -> str:
        return self._strategy_id

    def __repr__(self):
        return f'strategy.{self.get_id()}'


class StrategyRunner:
    def __init__(self, strategy: "Strategy"):
        self.strategy = strategy
        self.event_source_conf = settings.EVENT_SOURCE_CONF
        self.tasks = []

    def load_last_state(self):
        """load strategy state from database if exists"""
        # todo

    def save_state(self):
        """save strategy state"""
        # todo

    def create_monitor_task(self):
        async def _check():
            while True:
                for task in self.tasks:
                    if task.done():
                        logging.error(f"task {task.get_name()} has exited unexpectedly.")
                await asyncio.sleep(3)
        loop = asyncio.get_event_loop()
        loop.create_task(_check(), name=f'task.{self.strategy}.monitor')

    def create_schedule_task(self):
        async def _timer(i: int, callback: Callable):
            callback()
            while True:
                await asyncio.sleep(i)
                if inspect.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()

        loop = asyncio.get_event_loop()
        registry = self.strategy.__timer_registry__
        for interval, method_name in registry.items():
            method = getattr(self.strategy, method_name)
            t = loop.create_task(_timer(interval, method), name=f'task.{self.strategy}.timer({interval}')
            self.tasks.append(t)

    def create_listening_tasks(self):
        async def _create_task(e: "EventSource", c: Callable):
            while True:
                event = await e.get()
                if inspect.iscoroutinefunction(c):
                    await c(event)
                else:
                    c(event)

        loop = asyncio.get_event_loop()
        registry = self.strategy.__event_registry__
        for event_type, method_name in registry.items():
            event_source = self.event_source_conf.get(event_type)
            if event_source is None:
                logging.error(f'can not find event source of {event_type}.')
            method = getattr(self.strategy, method_name)
            t = loop.create_task(_create_task(event_source, method), name=f'task.{self.strategy}.wait.{event_type}')
            self.tasks.append(t)

    def create_tasks(self):
        self.create_listening_tasks()
        self.create_schedule_task()
        self.create_monitor_task()
