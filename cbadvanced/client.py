import datetime
import json
import uuid

import requests
from cbadvanced.cb_auth import CBAuth
from cbadvanced.exceptions import (
    AdvancedTradeAPIExceptions,
    AdvancedTradeRequestException)


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

    @staticmethod
    def _handle_response(response):
        """Internal helper for handling API responses from the COINBASE server.
        Raises the appropriate exceptions when necessary; otherwise, returns the
        response.

        Typical status codes

        400	Bad Request -- Invalid request format

        401	Unauthorized -- Invalid API Key

        403	Forbidden -- You do not have access to the requested resource

        404	Not Found

        500	Internal Server Error -- We had a problem with our server
        """
        if not str(response.status_code).startswith('2'):
            raise AdvancedTradeAPIExceptions(response)

        try:
            result = response.json()

            # by default return full response
            # if it's a normal response we have a data attribute, return that
            return result
        except ValueError:
            raise AdvancedTradeRequestException('Invalid Response: %s' % response.text)

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
        response = self.session.request(method, url, params=params, data=data,
                                        auth=self.auth, timeout=30)
        return self._handle_response(response)

    def get_accounts(self):
        return self.get_account('', limit='250')

    def get_account(self, account_id, **kwargs):
        return self._send_message('get', f'/brokerage/accounts/{account_id}', params=kwargs)

    def create_order(self, product_id: str, side: str, client_order_id: uuid = None, **kwargs):
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
                            start: int = int((datetime.datetime.now() - datetime.timedelta(hours=24)).timestamp()),
                            end: int = int(datetime.datetime.now().timestamp()),
                            granularity: str = 'FIFTEEN_MINUTE'):
        params = {'start': str(start),
                  'end': str(end),
                  'granularity': granularity}
        return self._send_message('get', f'/brokerage/products/{product_id}/candles', params=params)

    def get_market_trades(self, product_id: str, limit: int):
        params = {'limit': limit}
        return self._send_message('get', f'/brokerage/products/{product_id}/ticker', params=params)
