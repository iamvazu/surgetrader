from bittrex.bittrex import Bittrex
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

markets = b.get_market_summaries()
for market in markets['result']:
    pprint.pprint(market)
    market['PercentGain'] = percent_gain(market['High'], market['Low'])
    print "\t", market['MarketName'], market['PrevDay']

for market in sorted(markets['result'], key=lambda e: e['PercentGain']):
    print market['PercentGain'], market['MarketName'], market['High'], market['Low'], market['PrevDay']
