#!/usr/bin/env python


import logging
import pprint
from datetime import datetime

from db import db
import mybittrex

logger = logging.getLogger(__name__)

b = mybittrex.make_bittrex()

markets = b.get_market_summaries()

with open("markets.json", "w") as markets_file:
    markets_file.write(pprint.pformat(markets['result']))

for market in markets['result']:

    id = db.market.insert(
        name=market['MarketName'],
        ask=market['Ask'],
        timestamp=datetime.now()
        )


db.commit()
