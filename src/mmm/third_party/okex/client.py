import urllib.parse
import requests
import json
from datetime import datetime

from mmm.third_party.okex import consts as c, utils, exceptions


class Client(object):

    def __init__(self, api_key, api_secret_key, passphrase, use_server_time=True, flag='1'):

        self.API_KEY = api_key
        self.API_SECRET_KEY = api_secret_key
        self.PASSPHRASE = passphrase
        self.use_server_time = use_server_time
        self.flag = flag

    def _request(self, method, request_path, params):

        if method == c.GET:
            request_path = request_path + '?' + urllib.parse.urlencode(params)
        url = c.API_URL + request_path
        if not self.use_server_time:
            iso_time = utils.get_timestamp()
        else:
            timestamp = self._get_server_timestamp()
            server_time = datetime.utcfromtimestamp(timestamp/1000)
            iso_time = server_time.isoformat("T", "milliseconds") + 'Z'

        body = json.dumps(params) if method == c.POST else ""

        sign = utils.sign(utils.pre_hash(iso_time, method, request_path, body), self.API_SECRET_KEY)
        header = utils.get_header(self.API_KEY, sign, iso_time, self.PASSPHRASE, self.flag)

        response = None

        if method == c.GET:
            response = requests.get(url, headers=header)
        elif method == c.POST:
            response = requests.post(url, data=body, headers=header)

        if not str(response.status_code).startswith('2'):
            raise exceptions.OkexAPIException(response)

        return response.json()

    def _request_without_params(self, method, request_path):
        return self._request(method, request_path, {})

    def _request_with_params(self, method, request_path, params):
        params = {k: v for k, v in params.items() if v}
        return self._request(method, request_path, params)

    @classmethod
    def _get_server_timestamp(cls):
        url = c.API_URL + c.SERVER_TIMESTAMP_URL
        response = requests.get(url)
        if response.status_code == 200:
            return int(response.json()['data'][0]['ts'])
        else:
            return ""
