from mmm.core.datasource.okex.subscription import OKEXTrades, OKEXTradesResp, OKEXCandle, OKEXCandleResp
from mmm.core.strategy import Strategy
from mmm.credential import Credential
from mmm.core.strategy.decorators import sub, timer


class GridStrategy(Strategy):

    @sub(OKEXTrades('BTC-USDT-SWAP'))
    def on_trades(self, data: "OKEXTradesResp"):
        print(data)
        print('.'*20)

    @sub(OKEXCandle('candle1D', 'BTC-USDT-SWAP'))
    def on_orderbook(self, data: OKEXCandleResp):
        print(data)
        print('-'*20)

    @timer(3)
    def schedule(self):
        from datetime import datetime
        print(datetime.now())


strategy = GridStrategy(bot_id='bot.123', credential=Credential.load_from_env())
