from bittrex.bittrex import Bittrex
import json
import logging


logger = logging.getLogger(__name__)


with open("secrets.json") as secrets_file:
    secrets = json.load(secrets_file)
    b = Bittrex(secrets['key'], secrets['secret'])

print b.get_balance('BTC')
print dir(b)
