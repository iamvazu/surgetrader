import json
from bittrex.bittrex import Bittrex


def make_bittrex():
    with open("secrets.json") as secrets_file:
        secrets = json.load(secrets_file)
        b = Bittrex(secrets['key'], secrets['secret'])

    return b
