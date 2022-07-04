from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from mmm.core.datasource.okex.subscription import OKEXTradesResp, OKEXCandleResp
from mmm.core.datasource.parser import Parser, ParserFactory


class TradesParser(Parser):

    def parse(self, data: Dict) -> List["OKEXTradesResp"]:
        result = []
        data = data['data']
        for each in data:
            item = OKEXTradesResp(each['instId'], Decimal(each['px']), Decimal(each['sz']), each['side'],
                                  datetime.fromtimestamp(int(each['ts'])/1000), data)
            result.append(item)
        return result


class CandleParser(Parser):

    def parse(self, data) -> List["OKEXCandleResp"]:
        result = []
        for each in data['data']:
            bar = OKEXCandleResp(
                candle_type=data['arg']['channel'],
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


parser_factory = ParserFactory()
parser_factory.register('trades', TradesParser())
