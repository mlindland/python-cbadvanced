import json
import pprint
import uuid

import requests
from cb_auth import CBAuth


class Client:

    def __init__(self, key, b64secret):
        # "https://api.pro.coinbase.com"
        """ Create an instance of the AuthenticatedClient class.
        Args:
            key (str): Your API key.
            b64secret (str): The secret key matching your API key.
        """
        self.URL = 'https://api.coinbase.com/api/v3'
        self.auth = CBAuth(key, b64secret)
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
        return self.get_account('')

    def get_account(self, account_id):
        """ Get information for a single account.
        Use this endpoint when you know the account_id.
        Args:
            account_id (str): Account id for account you want to get.
        Returns:
            dict: Account information. Example::
                {
                    "id": "a1b2c3d4",
                    "balance": "1.100",
                    "holds": "0.100",
                    "available": "1.00",
                    "currency": "USD"
                }
        """
        return self._send_message('get', '/brokerage/accounts/' + account_id)

    def place_order(self, product_id, side, client_order_id=uuid.uuid1().__str__(), **kwargs):
        if client_order_id is None:
            raise ValueError('Client Order Id cannot be empty')

        # Build params dict
        params = {'side': side,
                  'product_id': product_id,
                  'client_order_id': client_order_id,
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

    def get_products(self):
        """Get a list of available currency pairs for trading.
        Returns:
            list: Info about all currency pairs. Example::
                [
                    {
                        "id": "BTC-USD",
                        "display_name": "BTC/USD",
                        "base_currency": "BTC",
                        "quote_currency": "USD",
                        "base_min_size": "0.01",
                        "base_max_size": "10000.00",
                        "quote_increment": "0.01"
                    }
                ]
        """
        return self._send_message('get', '/brokerage/products')
