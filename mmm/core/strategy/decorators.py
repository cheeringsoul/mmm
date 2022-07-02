import inspect

from functools import wraps
from typing import Union

from mmm.core.hub.datasource_msg_hub.subscription import Subscription


FloatInt = Union[float, int]


def timer(interval: "FloatInt"):
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


def sub(topic: "Subscription"):
    if not isinstance(topic, Subscription):
        raise TypeError('param topic must be type of Subscription.')

    def new_func(func):
        if hasattr(func, '__subscription__'):
            raise TypeError('You cannot decorate a function which already decorated with sub with the sub decorator.')

        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def wrap_func(self, event_data):
                return await func(self, event_data)
        else:
            @wraps(func)
            def wrap_func(self, event_data):
                return func(self, event_data)
        wrap_func.__subscription__ = topic
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
