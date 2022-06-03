from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Numeric, create_engine, Index, ForeignKey
from sqlalchemy.orm import declarative_base, declared_attr

from mmm.config import settings


Base = declarative_base()
engine = create_engine(settings.DATABASE, echo=True, future=True)


class Mixin:

    @declared_attr
    def __tablename__(cls):  # noqa
        return cls.__name__.lower()

    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Order(Base, Mixin):
    strategy = Column(Integer, ForeignKey("strategy.id"), doc='strategy')
    uniq_id = Column(String(64), doc='exchange name', unique=True)
    exchange = Column(String(16), doc='exchange name')
    order_id = Column(String(128), doc='order id')
    client_order_id = Column(String(128), doc='client order id')
    instrument_id = Column(String(16), doc='instrument id')
    currency = Column(String(16), doc='currency')
    order_type = Column(Integer, doc='order type, market: 1, limit: 2, post_only: 3, fok: 4, ioc: 5, optimal_limit_ioc:6')  # noqa
    side = Column(String(16), doc='side')
    avg_price = Column(Numeric(8, 16), doc='avg price')
    turnover = Column(Numeric(8, 16), doc='turnover')
    volume = Column(Numeric(8, 16), doc='volume')


class StrategyPosition(Base, Mixin):
    ...


class Strategy(Base, Mixin):
    ...

