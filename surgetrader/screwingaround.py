from bittrex.bittrex import Bittrex, SELL_ORDERBOOK
import json
import logging
import pprint


logger = logging.getLogger(__name__)


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    b = Bittrex(secrets['key'], secrets['secret'])

b.get_balance('BTC')

def percent_gain(high, low):
    increase = (high - low)
    if increase:
        percent_gain = increase / low
    else:
        percent_gain = 0
    return percent_gain

pprint.pprint(b.get_orderbook('BTC-SLING', SELL_ORDERBOOK))
