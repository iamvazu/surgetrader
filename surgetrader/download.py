from bittrex.bittrex import Bittrex
import json
import logging
import pprint
from datetime import datetime
import random

from db import db


logger = logging.getLogger(__name__)


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    b = Bittrex(secrets['key'], secrets['secret'])

markets = b.get_market_summaries()
for market in markets['result']:

    tmp = market['Low'] + random.uniform(-2, 2) * market['Low']

    id = db.market.insert(
        name=market['MarketName'],
        low=tmp,
        timestamp=datetime.now()
        )


db.commit()
