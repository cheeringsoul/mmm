from .client import Client
from .consts import *


class TradeAPI(Client):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    # Place Order
    def place_order(self, inst_id, td_mode, side, ord_type, sz, ccy=None,
                    cl_ord_id=None, tag=None, pos_side=None, px=None, reduce_only=None):
        params = {'instId': inst_id, 'tdMode': td_mode, 'side': side, 'ordType': ord_type, 'sz': sz, 'ccy': ccy,
                  'clOrdId': cl_ord_id, 'tag': tag, 'posSide': pos_side, 'px': px, 'reduceOnly': reduce_only}
        return self._request_with_params(POST, PLACE_ORDER, params)

    # Place Multiple Orders
    def place_multiple_orders(self, orders_data):
        return self._request_with_params(POST, BATCH_ORDERS, orders_data)

    # Cancel Order
    def cancel_order(self, inst_id, ord_id=None, cl_ord_id=None):
        params = {'instId': inst_id, 'ordId': ord_id, 'clOrdId': cl_ord_id}
        return self._request_with_params(POST, CANCEL_ORDER, params)

    # Cancel Multiple Orders
    def cancel_multiple_orders(self, orders_data):
        return self._request_with_params(POST, CANCEL_BATCH_ORDERS, orders_data)

    # Amend Order
    def amend_order(self, inst_id, cxl_on_fail=None, ord_id=None, cl_ord_id=None,
                    req_id=None, new_sz=None, new_px=None):
        params = {
            'instId': inst_id,
            'cxlOnFailc': cxl_on_fail,
            'ordId': ord_id,
            'clOrdId': cl_ord_id,
            'reqId': req_id,
            'newSz': new_sz,
            'newPx': new_px
        }
        return self._request_with_params(POST, AMEND_ORDER, params)

    # Amend Multiple Orders
    def amend_multiple_orders(self, orders_data):
        return self._request_with_params(POST, AMEND_BATCH_ORDER, orders_data)

    # Close Positions
    def close_positions(self, inst_id, mgn_mode, pos_side=None, ccy=None):
        params = {'instId': inst_id, 'mgnMode': mgn_mode, 'posSide': pos_side, 'ccy': ccy}
        return self._request_with_params(POST, CLOSE_POSITION, params)

    # Get Order Details
    def get_orders(self, inst_id, cl_ord_id=None, ord_id=None):
        params = {'instId': inst_id, 'ordId': ord_id, 'clOrdId': cl_ord_id}
        return self._request_with_params(GET, ORDER_INFO, params)

    # Get Order List
    def get_order_list(self, inst_type=None, uly=None, inst_id=None, ord_type=None,
                       state=None, after=None, before=None, limit=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id, 'ordType': ord_type, 'state': state,
                  'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDERS_PENDING, params)

    # Get Order History (last 7 days）
    def get_orders_history(self, inst_type, uly=None, inst_id=None, ord_type=None, state=None,
                           after=None, before=None, limit=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id, 'ordType': ord_type, 'state': state,
                  'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDERS_HISTORY, params)

    # Get Order History (last 3 months)
    def orders_history_archive(self, inst_type, uly=None, inst_id=None, ord_type=None,
                               state=None, after=None, before=None, limit=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id, 'ordType': ord_type, 'state': state,
                  'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDERS_HISTORY_ARCHIVE, params)

    # Get Transaction Details
    def get_fills(self, inst_type=None, uly=None, inst_id=None, ord_id=None, after=None, before=None, limit=None):
        params = {'instType': inst_type, 'uly': uly, 'instId': inst_id, 'ordId': ord_id,
                  'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDER_FILLS, params)

    # Place Algo Order
    def place_algo_order(self, inst_id, td_mode, side, ord_type, sz, ccy=None, pos_side=None, reduce_only=None,
                         tp_trigger_px=None, tp_ord_px=None, sl_trigger_px=None, sl_ord_Px=None,
                         trigger_px=None, order_px=None):
        params = {'instId': inst_id, 'tdMode': td_mode, 'side': side, 'ordType': ord_type, 'sz': sz, 'ccy': ccy,
                  'posSide': pos_side, 'reduceOnly': reduce_only, 'tpTriggerPx': tp_trigger_px, 'tpOrdPx': tp_ord_px,
                  'slTriggerPx': sl_trigger_px, 'slOrdPx': sl_ord_Px, 'triggerPx': trigger_px, 'orderPx': order_px}
        return self._request_with_params(POST, PLACE_ALGO_ORDER, params)

    # Cancel Algo Order
    def cancel_algo_order(self, params):
        return self._request_with_params(POST, CANCEL_ALGOS, params)

    # Get Algo Order List
    def order_algos_list(self, ord_type, algo_id=None, inst_type=None, inst_id=None, after=None,
                         before=None, limit=None):
        params = {'ordType': ord_type, 'algoId': algo_id, 'instType': inst_type, 'instId': inst_id, 'after': after,
                  'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDERS_ALGO_PENDING, params)

    # Get Algo Order History
    def order_algos_history(self, ord_type, state=None, algo_id=None, inst_type=None, inst_id=None, after=None,
                            before=None, limit=None):
        params = {'ordType': ord_type, 'state': state, 'algoId': algo_id, 'instType': inst_type, 'instId': inst_id,
                  'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, ORDERS_ALGO_HISTORY, params)
