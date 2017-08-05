# surgetrader
Trade on surges detected at BitTrex

# Script description



# Installation

Install python-bittrex from this github instead of PyPi.
`pip install -r requirements.txt`

# Configuration

in the `src` directory, `mybittrex.ini` should have key and secret in it like so

    [api]
    key = asdfa8asdf8asdfasdf
    secret = 99asdfn8sdfjasd

# Usage
## Cron

Create 1 cron entry that downloads the market data every hour (or whatever
sample period you like) and then scans for the coin with the strongest surge and buys it.

    00 * * * * cd $ST/src/ ; $PY download.py; $PY scan.py --buy 1

Creat another cron entry that sets a profit target on the successful buys

    */5 * * * * cd $ST/src/ ; $PY takeprofit.py --percent 10

# Earning Potential

Account balance = $1000

2% = 20

1% gain on 2% of the account = 20.20

therefore you are making 20 cents per trade

50 trades in a month = 10 dollars profit

10 dollars is 1% of 1000 -> 1% gain on the account

Therefore taking 50 2% trades and setting a 1% profit margin (ignoring fees)

# TODO

- Move percentage of BTC to trade on each run to config file.

- Take profit right after successful buy. There is no reason for takeprofit.py
to exist separately: just edit scan.py and have it take the profit!
