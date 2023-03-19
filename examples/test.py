from cbadvanced.client import Client
from cbadvanced.vars import ADVANCED_KEY, ADVANCED_SECRET
from pprint import pprint

if __name__ == '__main__':
    client = Client(key=ADVANCED_KEY, b64secret=ADVANCED_SECRET)
    pprint(client.get_market_trades('BTC-USD', 5))
