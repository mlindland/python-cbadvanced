import time

from cbadvanced.client import Client
from cbadvanced.vars import ADVANCED_KEY, ADVANCED_SECRET
from pprint import pprint

if __name__ == '__main__':
    client = Client(key=ADVANCED_KEY, b64secret=ADVANCED_SECRET)
    # result = client.get_accounts()
    result = client.place_order('ETH-BTC', 'BUY', price=0.063, size=0.001)
    pprint(result)
    time.sleep(2)
    result = client.cancel_orders(result['success_response']['order_id'])
    pprint(result)

