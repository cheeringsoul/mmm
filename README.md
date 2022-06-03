### 加密货币量化交易框架mmm(make-more-money), 持续完善中...
### Cryptocurrency quantitative trading framework, updating...

安装
pip install .

示例

```python
import asyncio
import json
import logging

from mmm.credential import Credential
from mmm.datasource import OkexWsDatasource
from mmm.order.executor import OrderExecutor
from mmm.strategy.core.base import StrategyRunner
from mmm.events.event import TradesEvent, OrderBookEvent
from mmm.strategy.core.base import Strategy
from mmm.strategy.core.decorators import sub_event, timer


class JfdStrategy(Strategy):

    @sub_event(TradesEvent)
    def on_ticker(self, ticker: TradesEvent):
        """"""
        print(ticker)
        print('.'*20)

    @sub_event(OrderBookEvent)
    def on_orderbook(self, order_book: OrderBookEvent):
        """"""
        print(order_book)
        print('-'*20)

    @timer(3)
    def schedule(self):
        from datetime import datetime
        print(datetime.now())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    topic1 = json.dumps({
        "op": "subscribe",
        "args": [{
            "channel": "trades",
            "instId": "BTC-USDT"
        }, {
            "channel": "books",
            "instId": "BTC-USDT"
        }]
    })
    OkexWsDatasource().subscribe(topic1)
    credential = Credential.load_from_env()
    StrategyRunner(JfdStrategy(credential)).create_tasks()
    OrderExecutor().create_task()
    asyncio.get_event_loop().run_forever()


```