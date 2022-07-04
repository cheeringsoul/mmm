from .client import Client
from .consts import *


class AccountAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='0'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # Get Positions
    def get_position_risk(self, inst_type=None):
        params = {}
        if inst_type:
            params['instType'] = inst_type
        return self._request_with_params(GET, POSITION_RISK, params)

    # Get Balance
    def get_account(self, ccy=None):
        params = {}
        if ccy:
            params['ccy'] = ccy
        return self._request_with_params(GET, ACCOUNT_INFO, params)

    # Get Positions
    def get_positions(self, inst_type=None, inst_id=None):
        params = {}
        if inst_type:
            params['instType'] = inst_type
        if inst_id:
            params['instId'] = inst_id
        return self._request_with_params(GET, POSITION_INFO, params)

    # Get Bills Details (recent 7 days)
    def get_bills_detail(self, inst_type=None, ccy=None, mgn_mode=None, ct_type=None,
                         _type=None, sub_type=None, after=None, before=None, limit=None):
        params = {'instType': inst_type, 'ccy': ccy, 'mgnMode': mgn_mode, 'ctType': ct_type, 'type': _type,
                  'subType': sub_type, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BILLS_DETAIL, params)

    # Get Bills Details (recent 3 months)
    def get_bills_details(self, inst_type=None, ccy=None, mgn_mode=None, ct_type=None,
                          _type=None, sub_type=None, after=None, before=None, limit=None):
        local_vars = locals()
        params = {}
        for var_name in ['instType', 'ccy', 'mgnMode', 'ctType', 'type', 'subType', 'after', 'before', 'limit']:
            var_value = local_vars.get(var_name)
            if var_value is not None:
                params[var_name] = var_value
        return self._request_with_params(GET, BILLS_ARCHIVE, params)

    # Get Account Configuration
    def get_account_config(self):
        return self._request_without_params(GET, ACCOUNT_CONFIG)

    # Get Account Configuration
    def get_position_mode(self, pos_mode):
        params = {'posMode': pos_mode}
        return self._request_with_params(POST, POSITION_MODE, params)

    # Get Account Configuration
    def set_leverage(self, lever, mgn_mode, inst_id=None, ccy=None, pos_side=None):
        params = {'lever': lever, 'mgnMode': mgn_mode, 'instId': inst_id, 'ccy': ccy, 'posSide': pos_side}
        return self._request_with_params(POST, SET_LEVERAGE, params)

    # Get Maximum Tradable Size For Instrument
    def get_maximum_trade_size(self, inst_id, td_mode, ccy=None, px=None):
        params = {'instId': inst_id, 'tdMode': td_mode, 'ccy': ccy, 'px': px}
        return self._request_with_params(GET, MAX_TRADE_SIZE, params)

    # Get Maximum Available Tradable Amount
    def get_max_avail_size(self, inst_id, td_mode, ccy=None, reduce_only=None):
        params = {'instId': inst_id, 'tdMode': td_mode, 'ccy': ccy, 'reduceOnly': reduce_only}
        return self._request_with_params(GET, MAX_AVAIL_SIZE, params)

    # Increase / Decrease margin
    def adjustment_margin(self, inst_id, pos_side, _type, amt):
        params = {'instId': inst_id, 'posSide': pos_side, 'type': _type, 'amt': amt}
        return self._request_with_params(POST, ADJUSTMENT_MARGIN, params)

    # Get Leverage
    def get_leverage(self, inst_id, mgn_mode):
        params = {'instId': inst_id, 'mgnMode': mgn_mode}
        return self._request_with_params(GET, GET_LEVERAGE, params)

    # Get the maximum loan of isolated MARGIN
    def get_max_load(self, inst_id, mgn_mode, mgn_ccy):
        params = {'instId': inst_id, 'mgnMode': mgn_mode, 'mgnCcy': mgn_ccy}
        return self._request_with_params(GET, MAX_LOAN, params)

    # Get Fee Rates
    def get_fee_rates(self, inst_type, inst_id=None, uly=None, category=None):
        params = {'instType': inst_type, 'instId': inst_id, 'uly': uly, 'category': category}
        return self._request_with_params(GET, FEE_RATES, params)

    # Get interest-accrued
    def get_interest_accrued(self, inst_id=None, ccy=None, mgn_mode=None, after=None, before=None, limit=None):
        params = {'instId': inst_id, 'ccy': ccy, 'mgnMode': mgn_mode, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, INTEREST_ACCRUED, params)

    # Get interest-accrued
    def get_interest_rate(self, ccy=None):
        params = {'ccy': ccy}
        return self._request_with_params(GET, INTEREST_RATE, params)

    # Set Greeks (PA/BS)
    def set_greeks(self, greeks_type):
        params = {'greeksType': greeks_type}
        return self._request_with_params(POST, SET_GREEKS, params)

    # Get Maximum Withdrawals
    def get_max_withdrawal(self, ccy=None):
        params = {}
        if ccy:
            params['ccy'] = ccy
        return self._request_with_params(GET, MAX_WITHDRAWAL, params)
