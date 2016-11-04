from bittrex.bittrex import Bittrex
import json
import logging
import pprint
from datetime import datetime

from db import db


logger = logging.getLogger(__name__)


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    b = Bittrex(secrets['key'], secrets['secret'])

markets = b.get_market_summaries()
for market in markets['result']:
    if market['MarketName'] != 'BTC-SLG':
        continue

    id = db.market.insert(
        name=market['MarketName'],
        low=market['Low'],
        timestamp=datetime.now()
        )
    print id
