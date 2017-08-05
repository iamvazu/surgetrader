#!/usr/bin/env python

# core
import collections
import logging
import pprint

# 3rd party
import argh
import ConfigParser
from retry import retry

# local
from db import db
import mybittrex
from bittrex.bittrex import SELL_ORDERBOOK


logger = logging.getLogger(__name__)


ignore_by_in = 'BTC-MUE BTC-UTC'
ignore_by_find = 'ETH- USDT-'.split()
max_orders_per_market = 2


def percent_gain(new, old):
    increase = (new - old)
    if increase:
        percent_gain = increase / old
    else:
        percent_gain = 0
    return percent_gain


def number_of_open_orders_in(b, market):
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



def analyze_gain(b, min_volume=0):

    recent = collections.defaultdict(list)

    markets = b.get_market_summaries(by_market=True)

    pprint.pprint(markets)

    # take the 2 most recent pricings for each market and store in the
    # list 'recent'

    # having_query = db.market.
    for row in db().select(
        db.market.ALL,
        groupby=db.market.name
    ):
        for market_row in db(db.market.name == row.name).select(
                db.market.ALL,
                orderby=~db.market.timestamp,
                limitby=(0, 2)
        ):
            recent[market_row.name].append(market_row)

    print "Number of markets = {0}".format(len(recent.keys()))
    # pprint.pprint(recent)

    gain = list()

    for name, row in recent.iteritems():

        print name

        try:
            if min_volume and markets[name]['BaseVolume'] < min_volume:
                print "Ignoring on low volume {0}".format(markets[name])
                continue
        except KeyError:
            print "KeyError locating " + name
            continue

        if name in ignore_by_in:
            print "\tIgnore by in: " + name
            continue

        leave = False
        for f in ignore_by_find:
            if name.find(f) > -1:
                print '\tIgnore by find: ' + name
                leave = True

        if leave:
            continue

        if number_of_open_orders_in(b, name) >= max_orders_per_market:
            print 'Max open orders: ' + name
            continue

        if row[0].ask < 100e-8:
            print 'Single or double satoshi coin: ' + name
            continue

        gain.append(
            (
                name,
                percent_gain(row[0].ask, row[1].ask),
                row[1].ask,
                row[0].ask,
                'https://bittrex.com/Market/Index?MarketName={0}'.format(name),
            )
        )

    # pprint.pprint(gain)
    gain = sorted(gain, key=lambda r: r[1], reverse=True)
    for i, _gain in enumerate(gain, start=1):
        print "{0}: {1}".format(i, pprint.pformat(_gain))
        db.picks.insert(
            market=_gain[0],
            old_price=_gain[2],
            new_price=_gain[3],
            gain=_gain[1]
        )
        if i > 10:
            break
    db.commit()
    return gain


def report_btc_balance(b):
    bal = b.get_balance('BTC')
    pprint.pprint(bal)
    return bal['result']


def available_btc(b):
    bal = report_btc_balance(b)
    avail = bal['Available']
    print "Available btc={0}".format(avail)
    return avail


def rate_for(b, mkt, btc):
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



def get_takeprofit(c):
    p = c.get('takeprofit', 'percent')
    return int(p)

def profitable_rate(entry, gain):

    x_percent = gain / 100.0
    tp = entry * x_percent + entry

    print("On an entry of {0:.8f}, TP={1:.8f} for a {2} percent gain".format(
        entry, tp, gain))

    return tp

def _buycoin(c, b, mkt, btc):
    "Buy into market using BTC. Current allocately 2% of BTC to each trade."

    print "I have {0} BTC available.".format(btc)

    btc *= 0.04

    print "I will trade {0} BTC.".format(btc)

    rate, amount_of_coin = rate_for(b, mkt, btc)

    print "I get {0} units of {1} at the rate of {2:.8f} BTC per coin.".format(
        amount_of_coin, mkt, rate)

    r = b.buy_limit(mkt, amount_of_coin, rate)
    if r['success']:
        print "Buy was a success = {}".format(r)
        takeprofit = get_takeprofit(c)
        new_rate = profitable_rate(rate, takeprofit)
        "Let sell  b.sell_limit(mkt, amount_of_coin, new_rate)"
        rs = b.sell_limit(mkt, amount_of_coin, new_rate)
        pprint.pprint(rs)


def buycoin(c, b, n, min_volume=0):
    "Buy top N cryptocurrencies."

    top = analyze_gain(b, min_volume=min_volume)[:n]
    print 'TOP {0}: {1}'.format(n, top)
    avail = available_btc(b)
    for market in top:
        print 'market: {0}'.format(market)
        _buycoin(c, b, market[0], avail)


def main(ini, my_btc=False, buy=0, min_volume=1):

    config_file = ini
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    b = mybittrex.make_bittrex(config)

    if my_btc:
        report_btc_balance()
    elif buy:
        buycoin(config, b, buy, min_volume)
    else:
        analyze_gain(min_volume)
        available_btc()

if __name__ == '__main__':
    argh.dispatch_command(main)
