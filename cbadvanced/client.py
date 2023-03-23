import datetime
import json
import pprint
import time
import uuid

import requests
from cbadvanced.cb_auth import CBAuth


class Client:

    def __init__(self, key, secret):
        # "https://api.coinbase.com/api/v3"
        """ Create an instance of the AuthenticatedClient class.
        Args:
            key (str): Your API key.
            secret (str): The secret key matching your API key.
        """
        self.URL = 'https://api.coinbase.com/api/v3'
        self.auth = CBAuth(key, secret)
        self.session = requests.Session()

    # def _handle_response(response):
    #     """Internal helper for handling API responses from the COINBASE server.
    #     Raises the appropriate exceptions when necessary; otherwise, returns the
    #     response.
    #     """
    # if not str(response.status_code).startswith('2'):
    #     raise KucoinAPIException(response)
    # try:
    #     res = response.json()
    #
    #     if 'code' in res and res['code'] != "200000":
    #         # raise KucoinAPIException(response)
    #
    #     if 'success' in res and not res['success']:
    #         # raise KucoinAPIException(response)
    #
    #     # by default return full response
    #     # if it's a normal response we have a data attribute, return that
    #     if 'data' in res:
    #         res = res['data']
    #     return res
    # except ValueError:
    #     raise KucoinRequestException('Invalid Response: %s' % response.text)

    def _send_message(self, method, endpoint, params=None, data=None):
        """Send API request.
        Args:
            method (str): HTTP method (get, post, delete, etc.)
            endpoint (str): Endpoint (to be added to base URL)
            params (Optional[dict]): HTTP request parameters
            data (Optional[str]): JSON-encoded string payload for POST
        Returns:
            dict/list: JSON response
        """
        url = self.URL + endpoint
        result = self.session.request(method, url, params=params, data=data,
                                      auth=self.auth, timeout=30)
        return result.json()

    def get_accounts(self):
        return self.get_account('', limit='250')

    def get_account(self, account_id, **kwargs):
        return self._send_message('get', f'/brokerage/accounts/{account_id}', params=kwargs)

    def create_order(self, product_id: str, side: str, client_order_id: uuid, **kwargs):
        # Build params dict
        if client_order_id is None:
            client_order_id = uuid.uuid4()
        params = {'side': side,
                  'product_id': product_id,
                  'client_order_id': client_order_id.__str__(),
                  'order_configuration': {
                      'limit_limit_gtc': {
                          'base_size': str(kwargs.get('size')),
                          'limit_price': str(kwargs.get('price'))
                      }
                  }}
        params.update(kwargs)
        return self._send_message('post', '/brokerage/orders', data=json.dumps(params))

    def cancel_orders(self, order_id: []):
        if not isinstance(order_id, list):
            order_id = [order_id]
        params = {'order_ids': order_id}
        return self._send_message('post', '/brokerage/orders/batch_cancel', data=json.dumps(params))

    def list_orders(self, **kwargs):
        return self._send_message('get', '/brokerage/orders/historical/batch', params=kwargs)

    def list_fills(self, **kwargs):
        return self._send_message('get', '/brokerage/orders/historical/fills', params=kwargs)

    def get_order(self, order_id, **kwargs):
        return self._send_message('get', f'/brokerage/orders/historical/{order_id}', params=kwargs)

    def list_products(self):
        return self.get_product('')

    def get_product(self, product_id: str):
        return self._send_message('get', f'/brokerage/products/{product_id}')

    def get_product_candles(self, product_id: str,
                            start: int = int((datetime.datetime.now() - datetime.timedelta(minutes=24)).timestamp()),
                            end: int = int(datetime.datetime.now().timestamp()),
                            granularity: str = 'FIFTEEN_MINUTE'):
        params = {'start': str(start),
                  'end': str(end),
                  'granularity': granularity}
        return self._send_message('get', f'/brokerage/products/{product_id}/candles', params=params)

    def get_market_trades(self, product_id: str, limit: int):
        params = {'limit': limit}
        return self._send_message('get', f'/brokerage/products/{product_id}/ticker', params=params)
