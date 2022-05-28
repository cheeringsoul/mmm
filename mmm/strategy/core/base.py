import asyncio
import inspect
import logging
from mmm.events.event import Event
from mmm.events import EventSource, default_event_source_conf, EventSourceConfig
from typing import Type, Dict, Callable

from mmm.order.manager import OrderManager, default_order_manager


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

    def __init__(self, order_manager: OrderManager = default_order_manager):
        self.order_manager = order_manager


class StrategyRunner:
    def __init__(self, strategy: "Strategy", event_source_conf: "EventSourceConfig" = default_event_source_conf):
        self.strategy = strategy
        self.event_source_conf = event_source_conf

    def create_schedule_task(self):
        async def timer(i: int, callback: Callable):
            callback()
            while True:
                await asyncio.sleep(i)
                if inspect.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()

        registry = self.strategy.__timer_registry__
        for interval, method_name in registry.items():
            loop = asyncio.get_event_loop()
            method = getattr(self.strategy, method_name)
            loop.create_task(timer(interval, method), name=f'{self.strategy}-timer({interval})-task')

    def create_listen_tasks(self):
        async def _create_task(e: "EventSource", c: Callable):
            while True:
                event = await e.get()
                if inspect.iscoroutinefunction(c):
                    await c(event)
                else:
                    c(event)

        registry = self.strategy.__event_registry__
        for event_type, method_name in registry.items():
            event_source = self.event_source_conf.get(event_type)
            if event_source is None:
                logging.error(f'{event_type}没有对应的事件源')
            loop = asyncio.get_event_loop()
            method = getattr(self.strategy, method_name)
            loop.create_task(_create_task(event_source, method), name=f'{self.strategy}-wait-for-{event_type}-task')

    def create_tasks(self):
        self.create_listen_tasks()
        self.create_schedule_task()
