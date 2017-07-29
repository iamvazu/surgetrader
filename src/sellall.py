#!/usr/bin/env python


import argh
import collections
import logging
import pprint
from retry import retry
from db import db
import mybittrex
from bittrex.bittrex import SELL_ORDERBOOK
from pprint import pprint


logger = logging.getLogger(__name__)
b = mybittrex.make_bittrex()

balances = b.get_balances()

for balance in balances['result']:
    if not balance['Available'] or balance['Currency'] == 'BTC':
        continue


    market = "BTC-" + balance['Currency']

    pprint(balance)

    ticker = b.get_ticker(market)['result']
    pprint(ticker)

    my_ask = ticker['Bid'] - 99e-8

    r = b.sell_limit(market, balance['Balance'], my_ask)
    pprint(r)
    print "--------------------"
