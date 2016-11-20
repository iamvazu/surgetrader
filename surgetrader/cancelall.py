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

orders = b.get_open_orders()

for order in orders['result']:
    pprint(order)
    r = b.cancel(order['OrderUuid'])
    pprint(r)
