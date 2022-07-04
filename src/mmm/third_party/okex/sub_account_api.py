from .client import Client
from .consts import *


class SubAccountAPI(Client):
    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=False, flag='1'):
        Client.__init__(self, api_key, api_secret_key, passphrase, use_server_time, flag)

    def balances(self, sub_acct):
        params = {"subAcct": sub_acct}
        return self._request_with_params(GET, BALANCE, params)

    def bills(self, ccy=None, _type=None, sub_acct=None, after=None, before=None, limit=None):
        params = {"ccy": ccy, 'type': _type, 'subAcct': sub_acct, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, BILLS, params)

    def delete(self, pwd, sub_acct, api_key):
        params = {'pwd': pwd, 'subAcct': sub_acct, 'apiKey': api_key}
        return self._request_with_params(POST, DELETE, params)

    def reset(self, pwd, sub_acct, label, api_key, perm, ip=None):
        params = {'pwd': pwd, 'subAcct': sub_acct, 'label': label, 'apiKey': api_key, 'perm': perm, 'ip': ip}
        return self._request_with_params(POST, RESET, params)

    def create(self, pwd, sub_acct, label, passphrase, perm=None, ip=None):
        params = {'pwd': pwd, 'subAcct': sub_acct, 'label': label, 'Passphrase': passphrase, 'perm': perm, 'ip': ip}
        return self._request_with_params(POST, CREATE, params)

    def view_list(self, enable=None, sub_acct=None, after=None, before=None, limit=None):
        params = {'enable': enable, 'subAcct': sub_acct, 'after': after, 'before': before, 'limit': limit}
        return self._request_with_params(GET, VIEW_LIST, params)

    def control_transfer(self, ccy, amt, _from, to, from_sub_account, to_sub_account):
        params = {'ccy': ccy, 'amt': amt, 'from': _from, 'to': to, 'fromSubAccount': from_sub_account,
                  'toSubAccount': to_sub_account}
        return self._request_with_params(POST, CONTROL_TRANSFER, params)
