import logging

from abc import ABCMeta, abstractmethod
from typing import Optional

from mmm.schema import Storage
from mmm.schema.models import Order, engine
from sqlalchemy.orm import Session

from mmm.project_types import OrderResult, Exchange, OrderStatus


logger = logging.getLogger(__name__)


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
        order.raw_data = order_result.raw_data
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


default_storage = SQLStorage()
