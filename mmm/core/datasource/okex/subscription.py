from abc import ABCMeta, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Dict

from mmm.core.hub.datasource_msg_hub.subscription import Subscription, ResponseOfSub
from mmm.project_types import Exchange


class OKEXSubscription(Subscription):
    def get_exchange(self) -> "Exchange":
        return Exchange.OKEX

    @abstractmethod
    def get_topic(self):
        """
        @return: args that send to okex.
        """


class OKEXResponseOfSub(ResponseOfSub):
    def get_exchange(self) -> "Exchange":
        return Exchange.OKEX


class OKEXTrades(OKEXSubscription):
    """https://www.okx.com/docs-v5/en/#websocket-api-public-channel-trades-channel"""

    def __init__(self, inst_id: str):
        self.inst_id = inst_id

    def equal_to(self, obj: "OKEXTrades"):
        return isinstance(obj, OKEXTrades) and self.inst_id == obj.inst_id

    def get_topic(self):
        return {
            "op": "subscribe",
            "args": [{
                "channel": "trades",
                "instId": self.inst_id
            }]
        }


class OKEXTradesResp(OKEXResponseOfSub):
    """https://www.okx.com/docs-v5/en/#websocket-api-public-channel-trades-channel"""

    def __init__(self, inst_id: str, price: Decimal, volume: Decimal, side: str, ts: datetime, origin_data: Dict):
        super().__init__(origin_data)
        self.inst_id: str = inst_id
        self.price: Decimal = price
        self.volume: Decimal = volume
        self.side: str = side
        self.ts: datetime = ts

    def response_for(self, obj: "Subscription") -> bool:
        return isinstance(obj, OKEXTrades) and obj.inst_id == self.inst_id


class OKEXCandle(OKEXSubscription):
    """https://www.okx.com/docs-v5/en/#websocket-api-public-channel-candlesticks-channel"""

    def equal_to(self, obj: "OKEXCandle"):
        return isinstance(obj, OKEXCandle) and obj.candle_type == self.candle_type and obj.inst_id == self.inst_id

    def __init__(self, candle_type, inst_id):
        self.candle_type = candle_type
        self.inst_id = inst_id

    def get_topic(self):
        return {
            "op": "subscribe",
            "args": [
                {
                    "channel": self.candle_type,
                    "instId": self.inst_id
                }
            ]
        }


class OKEXCandleResp(OKEXResponseOfSub):
    """https://www.okx.com/docs-v5/en/#websocket-api-public-channel-candlesticks-channel"""

    def __init__(self, candle_type: str, inst_id: str, ts: datetime, open_price: Decimal, high_price: Decimal,
                 low_price: Decimal, close_price: Decimal, volume: Decimal, volume_ccy: Decimal, origin_data: Dict):
        super().__init__(origin_data)
        self.candle_type: str = candle_type
        self.inst_id: str = inst_id
        self.ts: datetime = ts
        self.open_price: Decimal = open_price
        self.high_price: Decimal = high_price
        self.low_price: Decimal = low_price
        self.close_price: Decimal = close_price
        self.volume: Decimal = volume
        self.volume_ccy: Decimal = volume_ccy

    def response_for(self, obj: "Subscription") -> bool:
        return isinstance(obj, OKEXCandle) and obj.candle_type == self.candle_type and obj.inst_id == self.inst_id
