# core
import ConfigParser

# 3rd party

# local
from bittrex.bittrex import Bittrex


def make_bittrex():
    config_file = 'bittrex.ini'
    config = ConfigParser.RawConfigParser()
    config.read(config_file)

    with open("secrets.json") as secrets_file:
        secrets = json.load(secrets_file)
        b = Bittrex(config.get('api', 'key'), config.get('api', 'secret'))

    return b
