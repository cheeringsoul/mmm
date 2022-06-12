from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional


@dataclass
class Asset:
    inst_id: str
    amount: Decimal


class OrderType(Enum):
    MARKET = 1  # Market order
    LIMIT = 2  # Limit order
    POST_ONLY = 3  # Post only order
    FOK = 4  # Fill - or -kill order
    IOC = 5  # Immediate - or -cancel order
    OPTIMAL_LIMIT_IOC = 6  # Market Order with immediate - or -cancel order (applicable only to Futures and Perpetual swap).


class Exchange(Enum):
    BINANCE = 1
    OKEX = 2
    ...


class OrderStatus(Enum):
    CREATED = 0
    SUCCESS = 1
    FAILED = 2


@dataclass
class OrderResult:
    uniq_id: str
    exchange: "Exchange"
    strategy_name: str
    strategy_bot_id: str
    client_order_id: str
    order_params: dict
    status: "OrderStatus"
    order_id: str = ''
    msg: str = ''
    raw_data: Optional[dict] = None


