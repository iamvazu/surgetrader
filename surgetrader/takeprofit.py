#!/usr/bin/env python


# core
import logging
from datetime import datetime

# pypi
import argh
import collections
import logging
import pprint

import mybittrex
from bittrex.bittrex import SELL_ORDERBOOK

from db import db


# local

logging.basicConfig(
    format='%(lineno)s %(message)s',
    level=logging.WARN
)

one_percent = 1.0 / 100.0
two_percent = 2.0 / 100.0


logger = logging.getLogger(__name__)
b = mybittrex.make_bittrex()


def single_and_double_satoshi_scalp(price):
    # forget it - huge sell walls in these low-satoshi coins!
    return price + 2e-8


def _takeprofit(percent, row):
    entry = row.purchase_price

    x_percent = percent / 100.0
    tp = entry * x_percent + entry

    print("On an entry of {0:f}, TP={1:.8f} for a {2} percent gain".format(
        entry, tp, percent))

    r = b.sell_limit(row.market, row.amount, tp)
    pprint.pprint(r)

    row.update_record(selling_price=tp)


def takeprofit(p):

    print "Finding takeprofit rows..."
    for row in db(db.buy.selling_price == None).select():
        print "\t", row
        _takeprofit(p, row)

    db.commit()


def main(percent=10):

    takeprofit(percent)

if __name__ == '__main__':
    argh.dispatch_command(main)
