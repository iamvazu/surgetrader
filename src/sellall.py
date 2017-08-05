#!/usr/bin/env python


import ConfigParser
import argh
import collections
import logging
import pprint
from retry import retry
from db import db
import mybittrex
from bittrex.bittrex import SELL_ORDERBOOK
from pprint import pprint

def loop_forever():
    while True:
        pass


logger = logging.getLogger(__name__)


def cancelall(b):
    orders = b.get_open_orders()

    for order in orders['result']:
        pprint(order)
        r = b.cancel(order['OrderUuid'])
        pprint(r)



def sellall(b):
    cancelall(b)
    balances = b.get_balances()
    for balance in balances['result']:
        print "-------------------- {}".format(balance['Currency'])
        pprint(balance)

        if not balance['Available'] or balance['Currency'] == 'BTC':
            print "\tno balance or this is BTC"
            continue


        skipcoin = "CRYPT TIT GHC"
        if balance['Currency'] in skipcoin:
            print "\tthis is a skipcoin"
            continue

        market = "BTC-" + balance['Currency']

        pprint(balance)

        ticker = b.get_ticker(market)['result']
        pprint(ticker)

        my_ask = ticker['Bid'] - 5e-8

        print "My Ask = {}".format(my_ask)

        r = b.sell_limit(market, balance['Balance'], my_ask)
        pprint(r)


def main(ini):

    config_file = ini
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    b = mybittrex.make_bittrex(config)
    sellall(b)

if __name__ == '__main__':
    argh.dispatch_command(main)
