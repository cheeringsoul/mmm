import logging
from typing import Dict, Optional, Union

from mmm.core.hub.datasource_msg_hub.subscription import Subscription
from mmm.core.hub.inner_event_hub.event import OrderCreationEvent
from mmm.credential import Credential
from mmm.core.order.manager import OrderManager, DefaultOrderManager
from mmm.exceptions import SubscriptionError, TimerError
from mmm.project_types import Exchange


logger = logging.getLogger(__name__)


class SubRegistry:

    def __init__(self):
        self._registry: Dict["Subscription", str] = {}

    def exists(self, obj: "Subscription") -> bool:
        if not isinstance(obj, Subscription):
            return False
        for key, value in self._registry.items():
            if key.equal_to(obj):
                return True
        return False

    def register(self, s: "Subscription", method_name):
        self._registry[s] = method_name

    def get_subscriptions(self):
        return list(self._registry.keys())

    def items(self):
        return self._registry.items()


FloatInt = Union[float, int]


class TimerRegistry:
    def __init__(self):
        self._registry: Dict[FloatInt, str] = {}

    def exists(self, interval: FloatInt):
        for each in self._registry:
            return each == interval
        return False

    def register(self, interval, method_name):
        self._registry[interval] = method_name

    def items(self):
        return self._registry.items()


class StrategyMeta(type):
    def __new__(cls, name, bases, kwargs):  # noqa
        sub_registry = cls.__get_registry_from_base__(cls, bases, '__sub_registry__')
        if sub_registry is None:
            sub_registry = SubRegistry()

        timer_registry = cls.__get_registry_from_base__(cls, bases, '__timer_registry__')
        if timer_registry is None:
            timer_registry = TimerRegistry()

        for method_name, method in kwargs.items():
            subscription = getattr(method, '__subscription__', None)
            if subscription and sub_registry.exists(subscription):
                raise SubscriptionError(f"You can not sub {subscription.__name__} twice.")
            elif subscription:
                sub_registry.register(subscription, method_name)

            interval = getattr(method, '__timer_interval__', None)
            if interval and timer_registry.exists(interval):
                raise TimerError(f"You can not decorate timer({interval}) twice.")
            elif interval:
                timer_registry.register(interval, method_name)

        kwargs['__sub_registry__'] = sub_registry
        kwargs['__timer_registry__'] = timer_registry
        return super().__new__(cls, name, bases, kwargs)

    def __get_registry_from_base__(cls, bases, registry_name):  # noqa
        for each in bases:
            if getattr(each, registry_name):
                return getattr(each, registry_name)


class Strategy(metaclass=StrategyMeta):
    __sub_registry__: Optional["SubRegistry"] = None
    __timer_registry__: Optional["TimerRegistry"] = None

    def __init__(self, bot_id: str, credential: "Credential"):
        self.bot_id = bot_id
        self.credential = credential
        self.order_manager: OrderManager = DefaultOrderManager()

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
        event = OrderCreationEvent(
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

    @classmethod
    def get_strategy_name(cls):
        return f"{cls.__module__}.{cls.__name__}"

    @classmethod
    def get_sub_registry(cls):
        return cls.__sub_registry__

    @classmethod
    def get_timer_registry(cls):
        return cls.__timer_registry__

    @classmethod
    def get_subscriptions(cls):
        if cls.__sub_registry__:
            return cls.__sub_registry__.get_subscriptions()
        return []

    def __repr__(self):
        return f'strategy.{self.get_strategy_name()}'
