import collections
import logging
import pprint
from datetime import datetime
import random

from db import db


logger = logging.getLogger(__name__)


recent = collections.defaultdict(list)

for row in db().select(
        db.market.ALL,
        orderby=~db.market.timestamp
):
    if len(recent[row.name]) < 2:
        recent[row.name].append(row)

pprint.pprint(recent['BTC-SLING'])

print "recent is {0} entries".format(len(recent.keys()))

def percent_gain(high, low):
    increase = (high - low)
    if increase:
        percent_gain = increase / low
    else:
        percent_gain = 0
    return percent_gain

gain = list()

for name, rows in recent.iteritems():
    gain.append( (name, percent_gain(rows[0].low, rows[1].low)) )

pprint.pprint(gain)

gain = sorted(gain, key=lambda r: r[1])

pprint.pprint(gain)
