# core
import ConfigParser

# 3rd party

# local
from bittrex.bittrex import Bittrex


def make_bittrex(config):


    b = Bittrex(config.get('api', 'key'), config.get('api', 'secret'))

    return b
