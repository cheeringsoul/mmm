from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, create_engine, JSON, Text
from sqlalchemy.orm import declarative_base

from mmm.config import settings


Base = declarative_base()
engine = create_engine(settings.DATABASE, echo=True, future=True)


class Mixin:

    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB'}
    __mapper_args__ = {'always_refresh': True}

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Order(Base, Mixin):
    __tablename__ = 'order'

    uniq_id = Column(String(64), unique=True, nullable=False, doc='exchange name')
    strategy_bot_id = Column(String(128), unique=True, doc='table strategy_bot column strategy_bot_id')
    strategy_name = Column(String(128), nullable=False, doc='strategy name')
    exchange = Column(Integer, nullable=False, doc='BINANCE = 1, OKEX = 2')
    client_order_id = Column(String(128), nullable=False, doc='client order id')
    order_id = Column(String(128), doc='order id that exchange returned')
    order_params = Column(JSON, nullable=False, doc='order params')
    status = Column(Integer, nullable=False, doc='CREATED = 0, SUCCESS = 1, FAILED = 2')
    msg = Column(Text, doc='message')
    raw_data = Column(JSON, nullable=False, doc='data that exchange returned.')


class StrategyBotPosition(Base, Mixin):
    __tablename__ = 'strategy_bot_position'

    bot_id = Column(Integer, nullable=False, doc='strategy_bot id')
    instrument = Column(String(32), nullable=False, doc='instrument')


class StrategyBot(Base, Mixin):
    __tablename__ = 'strategy_bot'

    strategy_name = Column(String(128), nullable=False, doc='strategy name')
    strategy_bot_id = Column(String(128), unique=True)
    status = Column(String(8), doc='created、running、stopped、failed')
