from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from mmm.core.datasource.base import ParserFactory
from mmm.core.events.event import BarEvent, TradesEvent, OrderBookEvent, Event
from mmm.core.events.parser import Parser


class TradesParser(Parser):

    def parse(self, data: Dict) -> "TradesEvent" or List["TradesEvent"]:
        result = []
        data = data['data']
        for each in data:
            ticker = TradesEvent(each['instId'], Decimal(each['px']), Decimal(each['sz']), each['side'],
                                 datetime.fromtimestamp(int(each['ts'])/1000), data)
            result.append(ticker)
        return result


class BarParser(Parser):

    def parse(self, data) -> "BarEvent" or List["BarEvent"]:
        result = []
        for each in data['data']:
            bar = BarEvent(
                bar_type=data['arg']['channel'],
                inst_id=data['arg']['instId'],
                ts=datetime.fromtimestamp(int(each[0])/1000),
                open_price=Decimal(each[1]),
                high_price=Decimal(each[2]),
                low_price=Decimal(each[3]),
                close_price=Decimal(each[4]),
                volume=Decimal(each[5]),
                volume_ccy=Decimal(each[6]),
                origin_data=data
            )
            result.append(bar)
        return result


class OrderbookParser(Parser):

    def parse(self, data: Dict) -> "OrderBookEvent":
        return OrderBookEvent()  # todo


class DefaultParser(Parser):

    def parse(self, data: Dict) -> "Event" or List["Event"]:
        return data


parser_factory = ParserFactory()
parser_factory.register('trades', TradesParser())
parser_factory.register('books', OrderbookParser())
parser_factory.register('candle', BarParser())
