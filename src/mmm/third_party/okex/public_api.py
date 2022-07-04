from .client import Client
from .consts import *


class PublicAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # Get Instruments
    def get_instruments(self, inst_type, uly=None, inst_id=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id}
        return self._request_with_params(GET, INSTRUMENT_INFO, params)

    # Get Delivery/Exercise History
    def get_deliver_history(self, inst_type, uly, after=None, before=None, limit=None):
        params = {'instType': inst_type, 'uly': uly, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, DELIVERY_EXERCISE, params)

    # Get Open Interest
    def get_open_interest(self, inst_type, uly=None, inst_id=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id}
        return self._request_with_params(GET, OPEN_INTEREST, params)

    # Get Funding Rate
    def get_funding_rate(self, inst_id):
        params = {'instId': inst_id}
        return self._request_with_params(GET, FUNDING_RATE, params)

    # Get Funding Rate History
    def funding_rate_history(self, inst_id, after=None, before=None, limit=None):
        params = {'instId': inst_id, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, FUNDING_RATE_HISTORY, params)

    # Get Limit Price
    def get_price_limit(self, inst_id):
        params = {'instId': inst_id}
        return self._request_with_params(GET, PRICE_LIMIT, params)

    # Get Option Market Data
    def get_opt_summary(self, uly, exp_time=None):
        params = {'uly': uly, 'expTime': exp_time}
        return self._request_with_params(GET, OPT_SUMMARY, params)

    # Get Estimated Delivery/Excercise Price
    def get_estimated_price(self, inst_id):
        params = {'instId': inst_id}
        return self._request_with_params(GET, ESTIMATED_PRICE, params)

    # Get Discount Rate And Interest-Free Quota
    def discount_interest_free_quota(self, ccy=None):
        params = {'ccy': ccy}
        return self._request_with_params(GET, DISCOUNT_INTEREST_INFO, params)

    # Get System Time
    def get_system_time(self):
        return self._request_without_params(GET, SYSTEM_TIME)

    # Get Liquidation Orders
    def get_liquidation_orders(self, inst_type, mgn_mode=None, inst_id=None, ccy=None, uly=None,
                               alias=None, state=None, before=None, after=None, limit=None):
        params = {'instType': inst_type, 'mgnMode': mgn_mode, 'instId': inst_id, 'ccy': ccy, 'uly': uly,
                  'alias': alias, 'state': state, 'before': before, 'after': after, 'limit': limit}
        return self._request_with_params(GET, LIQUIDATION_ORDERS, params)

    # Get Mark Price
    def get_mark_price(self, inst_type, uly=None, inst_id=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id}
        return self._request_with_params(GET, MARK_PRICE, params)

    # Get Tier
    def get_tier(self, inst_type, td_mode, uly=None, inst_id=None, ccy=None, tier=None):
        params = {'instType': inst_type, 'tdMode': td_mode, 'uly': uly, 'instId': inst_id, 'ccy': ccy, 'tier': tier}
        return self._request_with_params(GET, MARK_PRICE, params)
