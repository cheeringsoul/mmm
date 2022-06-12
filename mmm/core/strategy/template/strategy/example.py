from mmm.credential import Credential
from mmm.core.events.event import TradesEvent, OrderBookEvent
from mmm.core.strategy.core.base import Strategy
from mmm.core.strategy.core.decorators import sub_event, timer


class GridStrategy(Strategy):

    @sub_event(TradesEvent)
    def on_ticker(self, ticker: TradesEvent):
        print(ticker)
        print('.'*20)

    @sub_event(OrderBookEvent)
    def on_orderbook(self, order_book: OrderBookEvent):
        print(order_book)
        print('-'*20)

    @timer(3)
    def schedule(self):
        from datetime import datetime
        print(datetime.now())


strategy = GridStrategy(bot_id='bot.123', credential=Credential.load_from_env())
