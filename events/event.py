from datetime import datetime
from decimal import Decimal


class Event:
    """策略事件"""


class TickerEvent(Event):

    def __init__(self, inst_id: str, price: Decimal, volume: Decimal, side: str, ts: datetime):
        self.inst_id: str = inst_id
        self.price: Decimal = price
        self.volume: Decimal = volume
        self.side: str = side
        self.ts: datetime = ts

    def __repr__(self):
        return f"<inst_id: {self.inst_id}, price: {self.price}, volume: {self.volume}, " \
               f"side: {self.side}, ts: {self.ts}>"


class OrderBookEvent(Event):

    def __init__(self):
        """"""


class BarEvent(Event):

    def __init__(self):
        """"""


class Bar1MEvent(BarEvent):
    """"""












