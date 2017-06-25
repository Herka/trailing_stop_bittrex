from BittrexWrapper import Bittrex
from portfolio import Portfolio
import time

class Trading:

	TRAIL_PERCENT = 0.05

	def __init__(self, api_key, api_secret):
		self.bt = Bittrex(api_key=api_key, api_secret = api_secret)
		self.p = Portfolio(api_key=api_key, api_secret = api_secret)
		self.open_orders = p.report()


	def update_prices:
		"""Get the LastPrice and update the DataFrame"""
		for i,r in self.open_orders.iterrows():
			market = "BTC-%s" % r["Currency"]
			ticker = bt.get_ticket(market):
			if ticker["success"]:
				last = ticker["result"]["Last"]
				self.open_orders.loc[self.open_orders["Currency"]==r["Currency"],"LastPrice" ] = last

			else:
				break
		return

	def update_stop(self):
		"""Update already existing Trailing-Stops and create new ones.
		If stop already exists it will be moved up if the last price was up.
		If it does not exist but minimum return was reached a new stop will be added"""

		for i, r in self.open_orders.loc[self.open_orders["Stop"]].iterrows():
			if r["LastPrice"] * (1-self.TRAIL_PERCENT) > r["Stop"]:
				self.open_orders.loc[i,"Stop"] = r["LastPrice"] * (1-self.TRAIL_PERCENT)

		for i, r in self.open_orders.loc[self.open_orders["LastPrice"] >= self.open_orders["MinReturn"]]:
			self.open_orders.loc[i, "Stop"] = r["LastPrice"] * (1 - self.TRAIL_PERCENT)
		return


	def close_order(self):
		for i, r in self.open_orders.iterrows():
			currency = r["Currency"]
			market = "BTC-%s" % currency
			quantity = r["Volume"]
 			self.bt.sell_market(market = market,quantity = quantity)
		return

	def monitoring(self):
		"""
		Monitores the last price, stop prices and looks for sell signals.
		:return:
		"""

		while True:
			self.update_prices()


			if self.open_orders.loc[(self.open_orders["Stop"])|(self.open_orders["LastPrice"] >= self.open_orders["MinReturn"])]:
				self.update_stop()

			if self.open_orders[self.open_orders["Stop"]<= self.open_orders["LastPrice"]]
				self.close_order()
			time.sleep(30)



if __name__ == "__main__":
	import sys
	api_key = sys.argv[1]
	api_secret = sys.argv[2]
	t = Trading(api_key, api_secret)