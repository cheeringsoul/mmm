from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


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


@dataclass
class Order:
    exchange: "Exchange"
    order_id: str
    client_order_id: str
    instrument_id: str
    currency: str
    order_type: "OrderType"
    side: str
    avg_price: Decimal
    turnover: Decimal
    volume: Decimal
