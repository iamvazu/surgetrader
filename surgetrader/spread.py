#!/usr/bin/env python


import argh
import collections
import logging
import pprint
from retry import retry
from db import db
import mybittrex
from bittrex.bittrex import SELL_ORDERBOOK


logger = logging.getLogger(__name__)
b = mybittrex.make_bittrex()

ignore_by_in = 'USDT-BTC BTC-ZEC BTC-ETH BTC-ETH BTC-MTR BTC-UTC BTC-XRP'
ignore_by_find = 'ETH-'
max_orders_per_market = 2


def percent_gain(new, old):
    increase = (new - old)
    if increase:
        percent_gain = increase / old
    else:
        percent_gain = 0
    return percent_gain


def number_of_open_orders_in(market):
    orders = list()
    oo = b.get_open_orders(market)['result']
    if oo:
        # pprint.pprint(oo)
        for order in oo:
            if order['Exchange'] == market:
                orders.append(order)
        return len(orders)
    else:
        return 0


def ignorable_market(bid, name):
    if bid < 100e-8:
        return True

    if name in ignore_by_in:
        return True

    if name.find(ignore_by_find) != -1:
        return True

    return False

def analyze_spread():

    Market = collections.namedtuple('Market',
                                    'name spread volume')
    markets = list()

    for market in b.get_market_summaries()['result']:

        if ignorable_market(market['Bid'], market['MarketName']):
            continue

        btc_volume = market['Bid'] * market['Volume']
        markets.append(
            Market(
                market['MarketName'],
                market['Ask'] - market['Bid'],
                btc_volume
            )
        )

    markets.sort(key=lambda m: (m.spread, -m.volume,))

    pprint.pprint(markets)


def report_btc_balance():
    bal = b.get_balance('BTC')
    pprint.pprint(bal)
    return bal['result']


def available_btc():
    bal = report_btc_balance()
    avail = bal['Available']
    print "Available btc={0}".format(avail)
    return avail


def rate_for(mkt, btc):
    "Return the rate that works for a particular amount of BTC."

    coin_amount = 0
    btc_spent = 0
    orders = b.get_orderbook(mkt, SELL_ORDERBOOK)
    for order in orders['result']:
        btc_spent += order['Rate'] * order['Quantity']
        if btc_spent > btc:
            break

    coin_amount = btc / order['Rate']
    return order['Rate'], coin_amount


@retry()
def record_buy(mkt, rate, amount):
    db.buy.insert(market=mkt, purchase_price=rate, amount=amount)
    db.commit()


def _buycoin(mkt, btc):
    "Buy into market using BTC. Current allocately 2% of BTC to each trade."

    print "I have {0} BTC available.".format(btc)

    btc *= 0.02

    print "I will trade {0} BTC.".format(btc)

    rate, amount_of_coin = rate_for(mkt, btc)

    print "I get {0} unit of {1} at the rate of {2} BTC per coin.".format(
        amount_of_coin, mkt, rate)

    r = b.buy_limit(mkt, amount_of_coin, rate)
    if r['success']:
        record_buy(mkt, rate, amount_of_coin)
    pprint.pprint(r)


def buycoin(n):
    "Buy top N cryptocurrencies."

    top = analyze_gain()[:n]
    print 'TOP {0}: {1}'.format(n, top)
    avail = available_btc()
    for market in top:
        print 'market: {0}'.format(market)
        _buycoin(market[0], avail)


def main(my_btc=False, buy=0):
    if my_btc:
        report_btc_balance()
    elif buy:
        buycoin(buy)
    else:
        analyze_spread()


if __name__ == '__main__':
    argh.dispatch_command(main)
