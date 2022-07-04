from .client import Client
from .consts import *


class MarketAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # Get Tickers
    def get_tickers(self, inst_type, uly=None):
        if uly:
            params = {'instType': inst_type, 'uly': uly}
        else:
            params = {'instType': inst_type}
        return self._request_with_params(GET, TICKERS_INFO, params)

    # Get Ticker
    def get_ticker(self, inst_id):
        params = {'instId': inst_id}
        return self._request_with_params(GET, TICKER_INFO, params)

    # Get Index Tickers
    def get_index_ticker(self, quote_ccy=None, instId=None):
        params = {'quoteCcy': quote_ccy, 'instId': instId}
        return self._request_with_params(GET, INDEX_TICKERS, params)

    # Get Order Book
    def get_orderbook(self, inst_id, sz=None):
        params = {'instId': inst_id, 'sz': sz}
        return self._request_with_params(GET, ORDER_BOOKS, params)

    # Get Candlesticks
    def get_candlesticks(self, inst_id, after=None, before=None, bar=None, limit=None):
        params = {'instId': inst_id, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, MARKET_CANDLES, params)

    # GGet Candlesticks History（top currencies only）
    def get_history_candlesticks(self, inst_id, after=None, before=None, bar=None, limit=None):
        params = {'instId': inst_id, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, HISTORY_CANDLES, params)

    # Get Index Candlesticks
    def get_index_candlesticks(self, inst_id, after=None, before=None, bar=None, limit=None):
        params = {'instId': inst_id, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, INDEX_CANDLES, params)

    # Get Mark Price Candlesticks
    def get_mark_price_candlesticks(self, inst_id, after=None, before=None, bar=None, limit=None):
        params = {'instId': inst_id, 'after': after, 'before': before, 'bar': bar, 'limit': limit}
        return self._request_with_params(GET, MARK_PRICE_CANDLES, params)

    # Get Index Candlesticks
    def get_trades(self, inst_id, limit=None):
        params = {'instId': inst_id, 'limit': limit}
        return self._request_with_params(GET, MARKET_TRADES, params)

    # Get Volume
    def get_volume(self):
        return self._request_without_params(GET, VOLUME)

    # Get Oracle
    def get_oracle(self):
        return self._request_without_params(GET, ORACLE)

    # Get Tier
    def get_tier(self, inst_type=None, td_mode=None, uly=None, inst_id=None, ccy=None, tier=None):
        params = {'instType': inst_type, 'tdMode': td_mode, 'uly': uly, 'instId': inst_id, 'ccy': ccy, 'tier': tier}
        return self._request_with_params(GET, TIER, params)
