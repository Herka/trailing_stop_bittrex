Adds a Trailing-Stop Feature for Bittrex.

Start with python bot.py APIKEY APISECRET


"Minimum return" defines the point where the Trailing-Stop will be activated and the TRAIL_PERCENT are the percentage points the stop order be moved along the changing price.
Once the price is smaller or equal to the stop order the sell will be activated and the bot tries to sell all coins for the "last price".
It loops until all coin are gone and changes the sell price according the the "LastPrice" every 30 seconds.
