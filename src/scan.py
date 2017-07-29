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

ignore_by_in = 'BTC-ZEC BTC-ETH BTC-ETH BTC-MTR BTC-UTC'
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



def analyze_gain(min_volume=0):

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
            print "Ignore by in: " + name
            continue

        if name.find(ignore_by_find) > -1:
            print 'Ignore by find: ' + name
            continue

        if number_of_open_orders_in(name) >= max_orders_per_market:
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


def buycoin(n, min_volume=0):
    "Buy top N cryptocurrencies."

    top = analyze_gain(min_volume=min_volume)[:n]
    print 'TOP {0}: {1}'.format(n, top)
    avail = available_btc()
    for market in top:
        print 'market: {0}'.format(market)
        _buycoin(market[0], avail)


def main(my_btc=False, buy=0, min_volume=1):
    if my_btc:
        report_btc_balance()
    elif buy:
        buycoin(buy, min_volume)
    else:
        analyze_gain(min_volume)
        available_btc()

if __name__ == '__main__':
    argh.dispatch_command(main)
