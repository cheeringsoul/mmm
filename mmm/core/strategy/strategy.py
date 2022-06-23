import logging
from typing import Type, Dict

from mmm.credential import Credential
from mmm.core.events.event import Event, OrderEvent
from mmm.core.order.manager import OrderManager, DefaultOrderManager
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
