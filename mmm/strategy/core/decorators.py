from functools import wraps
from typing import Type
from mmm.events import Event


def timer(interval: int):
    """
    定时任务
    :param interval: 时间间隔，单位：秒
    :return:
    """
    if not isinstance(interval, int):
        raise TypeError(f'参数interval必须是整数')

    def new_func(func):
        @wraps(func)
        def wrap_func(self):
            return func(self)
        wrap_func.__timer_interval__ = interval
        return wrap_func
    return new_func


def sub_event(event: Type[Event]):
    if not issubclass(event, Event):
        raise TypeError(f'sub_event参数必须是Event类型')

    def new_func(func):
        @wraps(func)
        def wrap_func(self, event_data):
            return func(self, event_data)
        wrap_func.__sub_event__ = event
        return wrap_func
    return new_func
