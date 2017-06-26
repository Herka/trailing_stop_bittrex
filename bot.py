from BittrexWrapper import Bittrex
from portfolio import Portfolio
import time

class Trading:

	TRAIL_PERCENT = 0.05


	def __init__(self, api_key, api_secret, minimum_return = 100):
		self.bt = Bittrex(api_key=api_key, api_secret = api_secret)
		self.p = Portfolio(api_key=api_key, api_secret = api_secret, minimum_return=minimum_return)
		self.open_orders = self.p.report()


	def update_prices(self):
		"""Get the LastPrice and update the DataFrame"""
		for i,r in self.open_orders.iterrows():
			market = "BTC-%s" % r["Currency"]
			ticker = self.bt.get_ticker(market)
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
		df = self.open_orders.loc[(self.open_orders["LastPrice"] >= self.open_orders["MinReturn"])|(~self.open_orders["Stop"].isnull())]
		for i, r in df.iterrows():
			self.open_orders.loc[i, "Stop"] = r["LastPrice"] * (1 - self.TRAIL_PERCENT)
		return

	def get_rate(self, market):
		rate = self.bt.get_ticker(market)
		if rate["success"] == True:
			return rate["result"]["Last"]
		else:
			time.sleep(30)
			self.get_rate(market)


	def close_order(self):
		for i, r in self.open_orders.loc[self.open_orders["Stop"]<= self.open_orders["LastPrice"]].iterrows():
			currency = r["Currency"]
			market = "BTC-%s" % currency
			quantity = r["Volume"]
			rate = self.get_rate(market)
			self.bt.sell_limit(market=market, quantity=quantity, rate=rate)
			time.sleep(15)
			while True:
				orders = self.bt.get_open_orders(market=market)
				if orders["success"] == "True":
					orders = pd.DataFrame(orders["result"])
					if orders.empty:
						break
					else:
						uid = open_order["result"][0]["OrderUuid"]
						self.bt.cancel(uuid=uid)
				rate = self.get_rate(market)
				self.bt.sell_limit(market = market,quantity = quantity, rate = rate)
				time.sleep(30)

		return


	def monitoring(self):
		"""
		Monitores the last price, stop prices and looks for sell signals.
		:return:
		"""

		while True:
			self.update_prices()
			self.open_orders = self.p.report()
			print (self.open_orders)
			if not self.open_orders.empty:
				if not self.open_orders.loc[(self.open_orders["LastPrice"] >= self.open_orders["MinReturn"])].empty:
					self.update_stop()
				if not self.open_orders["Stop"].dropna().empty:
					self.update_stop()
				if not self.open_orders.loc[self.open_orders["Stop"]>= self.open_orders["LastPrice"]].empty:
					self.close_order()
					time.sleep(5)
					self.open_orders = self.p.report()
			time.sleep(30)



if __name__ == "__main__":
	import sys
	api_key = sys.argv[1]
	api_secret = sys.argv[2]
	t = Trading(api_key, api_secret, minimum_return = 100)
	t.monitoring()