import inspect

from functools import wraps
from typing import Type

from mmm.core.events.event import Event


def timer(interval: int):
    """
    :param interval: seconds
    :return:
    """
    if not isinstance(interval, int):
        raise TypeError(f'interval must be int')

    def new_func(func):
        @wraps(func)
        def wrap_func(self):
            return func(self)
        wrap_func.__timer_interval__ = interval
        return wrap_func
    return new_func


def sub_event(event: Type[Event]):
    if not issubclass(event, Event):
        raise TypeError(f'event must be type of Event.')

    def new_func(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrap_func(self, event_data):
                return await func(self, event_data)
        else:
            @wraps(func)
            def wrap_func(self, event_data):
                return func(self, event_data)
        wrap_func.__sub_event__ = event
        return wrap_func
    return new_func


def register_handler(command):
    def new_func(func):
        if inspect.iscoroutinefunction(func):
            async def wrap_func(self, *args, **kwargs):
                return await func(self, *args, **kwargs)
        else:
            @wraps(func)
            def wrap_func(self, *args, **kwargs):
                return func(self, *args, **kwargs)
        wrap_func.__command__ = command
        return wrap_func
    return new_func
