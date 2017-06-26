import pandas as pd
from BittrexWrapper import Bittrex

class Portfolio(object):

	def __init__(self, api_key, api_secret):
		self.bt = Bittrex()
		self.bt.api_key = api_key
		self.bt.api_secret = api_secret
		self.open_orders  = pd.DataFrame()
		pass

	def report(self):
		self.min_return()
		return self.open_orders

	def get_open_orders(self):
		"""First get the Balances to see what open positions exist.
		Than loop through every open position to get the BuyPrice.
		"""
		self.open_orders = pd.DataFrame(columns=["Currency", "BuyPrice", "Volume","Stop", "LastPrice"])
		balances = self.bt.get_balances()
		if balances["success"]:
			balances = pd.DataFrame(balances["result"])
			balances = balances.loc[balances.Balance > 0]
			#OrderPrices
			for i, r in balances.iterrows():
				currency = r["Currency"]
				volume = r["Balance"]
				price = self.buy_price(currency, volume)
				order = pd.DataFrame([[currency, price, volume]], columns = ["Currency", "BuyPrice", "Volume"])
				self.open_orders = pd.concat([self.open_orders, order])
			self.open_orders = self.open_orders.loc[~self.open_orders["Currency"].isin(["BTC", "ETH"])]
		return

	def buy_price(self, currency, volume):
		"""Gets the average buying price for a open position."""
		market = "BTC-%s" % currency
		orderhistory = self.bt.get_order_history(market=market)
		if orderhistory["success"]:
			orderhistory = pd.DataFrame(orderhistory["result"], )
			orderhistory["Closed"] = pd.to_datetime(orderhistory["Closed"])
			orderhistory = orderhistory.loc[orderhistory["OrderType"] == "LIMIT_BUY"]
			orderhistory = orderhistory.sort_values("Closed", ascending=False)
			orderhistory.reset_index(drop=True, inplace=True)
			orderhistory.loc[:, "CumulativeQuant"] = orderhistory.Quantity.cumsum()
			orderhistory = orderhistory.loc[orderhistory.CumulativeQuant <= volume]
			price = sum(orderhistory.PricePerUnit * orderhistory.Quantity) / volume
			return price

	def min_return(self, min_return = 2):
		"""Defines the minimum return at what point the stop-limit will be activated.
		By default 2x."""
		if self.open_orders.empty:
			self.get_open_orders()
		self.open_orders.loc[:,"MinReturn"] = min_return * self.open_orders.BuyPrice
