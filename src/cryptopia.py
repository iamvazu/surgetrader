#!/usr/bin/env python3


import argh
import collections
import logging
import pprint
# from retry import retry
# from db import db
from bitex import Cryptopia




logger = logging.getLogger(__name__)

def scan(e):
    t = e.markets(baseMarket='BTC')
    # print(t.json())
    markets = sorted(t.json()['Data'], key=lambda k: k['Change'], reverse=True)

    count = 0

    for market in markets:
        if market['Change'] > 99:
            print(market)
            count += 1

    print("{} markets available to trade in.".format(count))


def main(my_btc=False, exchange='Cryptopia', buy=0, min_volume=1):

    key_file = '{}.key'.format(exchange.lower())
    e = Cryptopia(key_file=key_file)

    scan(e)

if __name__ == '__main__':
    argh.dispatch_command(main)
