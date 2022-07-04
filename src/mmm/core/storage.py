import logging

from abc import ABCMeta, abstractmethod
from sqlalchemy.orm import Session
from typing import Optional

from mmm.schema import Bot, Order, engine
from mmm.project_types import OrderResult, Exchange, OrderStatus


logger = logging.getLogger(__name__)


class Storage(metaclass=ABCMeta):

    @abstractmethod
    def save_order(self, order_result: "OrderResult"): ...

    @abstractmethod
    def query_order(self, uniq_id: str) -> Optional["OrderResult"]: ...

    @abstractmethod
    def create_or_update_bot(self, bot_id, **kwargs): ...


class SQLStorage(Storage):
    def save_order(self, order_result: "OrderResult"):
        order = Order()
        order.order_id = order_result.order_id
        order.client_order_id = order_result.client_order_id
        order.uniq_id = order_result.uniq_id
        order.strategy_bot_id = order_result.strategy_bot_id
        order.exchange = order_result.exchange.value
        order.status = order_result.status.value
        order.msg = order_result.msg
        order.order_params = order_result.order_params
        order.strategy_name = order_result.strategy_name
        order.raw_data = order_result.exchange_resp
        with Session(engine) as session:
            try:
                session.add(order)
            except Exception as e:  # noqa
                logger.exception(e)
                session.rollback()
            else:
                session.commit()

    def query_order(self, uniq_id: str) -> Optional["OrderResult"]:
        with Session(engine) as session:
            rv: Order = session.query(Order).filter_by(uniq_id=uniq_id).first()
            if not rv:
                return None
            return OrderResult(
                uniq_id=rv.uniq_id,
                exchange=Exchange(rv.exchange),
                strategy_name=rv.strategy_name,
                strategy_bot_id=rv.strategy_bot_id,
                client_order_id=rv.client_order_id,
                order_params=rv.order_params,
                status=OrderStatus(rv.status),
                order_id=rv.order_id,
                msg=rv.msg
            )

    def create_or_update_bot(self, bot_id, **kwargs):
        with Session(engine) as session:
            rv = session.query(Bot).filter_by(bot_id=bot_id).first()
            if rv:
                for key, value in kwargs.items():
                    setattr(rv, key, value)
            else:
                bot = Bot(bot_id=bot_id, **kwargs)
                session.add(bot)
            try:
                session.commit()
            except Exception as e:
                session.rollback()
                logger.exception(e)


default_storage = SQLStorage()
