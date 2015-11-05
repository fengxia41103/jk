from numpy import mean, std 
from collections import OrderedDict
from stock.models import *

class MySimulation(object):
	def __init__(self,user,data,historicals,capital,per_buy,buy_cutoff,sell_cutoff,category):
		self.user = user
		self.data = data
		self.historicals = historicals
		self.capital = capital
		self.per_buy = per_buy
		self.buy_cutoff = buy_cutoff
		self.sell_cutoff = sell_cutoff
		self.category = category	
		self.snapshot = OrderedDict()

	def run(self):
		# clear all positions and reset porfolio cash
		MyPosition.objects.filter(category=self.category).delete()

		# asset simulation result
		assets = {}
		equity = {}
		cash = {}
		
		# trading
		for on_date,symbols_by_rank in self.data:
			print on_date.isoformat()
			positions = None		
			total_symbols = len(symbols_by_rank)

			# record transactions
			self.snapshot[on_date] = {
				'cash': 0,
				'equity': 0,
				'asset': 0,
				'portfolio':[],
				'transaction':{'buy':[],'sell':[]}, 
				'gain':{'hold':0,'sell':0}
			}

			self.sell(on_date, symbols_by_rank)
			self.buy(on_date, symbols_by_rank)

			# compute equity, cash, asset
			positions = MyPosition.objects.filter(category = self.category, is_open = True).values('stock__symbol','position','vol')
			temp = []
			for p in positions:
				if p['stock__symbol'] in self.historicals[on_date]:
					# if symbol's historicals are missing for some reason
					# eg. stopped trading on that day, compay got bought
					# this would result some open position at the end of portfolio
					his = self.historicals[on_date][p['stock__symbol']]

					# we compute equity value based on daily close price
					if 'adj_close' in his and his['adj_close'] > 0: simulated_spot = his['adj_close'] 
					elif 'close_price' in his: simulated_spot = his['close_price']
				else:
					print p['stock__symbol'], 'not in historical!'
					continue

				temp.append(p['vol'] * simulated_spot)
				self.snapshot[on_date]['gain']['hold'] += p['vol'] * (simulated_spot - p['position'])

			equity[on_date] = sum(temp)
			cash[on_date] = self.capital
			assets[on_date] = equity[on_date] + cash[on_date]
			
			self.snapshot[on_date]['cash'] = cash[on_date]
			self.snapshot[on_date]['equity'] = equity[on_date]
			self.snapshot[on_date]['asset'] = assets[on_date]
			self.snapshot[on_date]['portfolio'] = positions

		on_dates = [on_date for on_date,symbols in self.data]
		cashes = [float(cash[d]) for d in on_dates]
		equities = [float(equity[d]) for d in on_dates]
		assets = [float(assets[d]) for d in on_dates]

		return {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets, 'snapshots':self.snapshot}

	def buy(self, **kargs):
		pass

	def sell(self,**kargs):
		pass

class MySimulationAlpha(MySimulation):
	"""
	Trading strategy:

	1. Stocks are ranked by a pre-calculated index value
	2. Buy stocks whose rank is above the buy_cutoff band, eg. if buy_cutoff = 0.25 and total samples = 20, buy if rank <= 0.25*20=5
	3. Sell stocks when it falls out the sell_cutoff band, eg. if sell_cutoff = 0.75 and total samples = 20, sell if rank >= (1-0.75)*20 = 5

	We simulate trades based on this strategy, then monitor the porfolio value (equity+cash).

	@param user: request.user
	@param data: a list of dict, [{'on_date':date obj, 'ranks':['symbol 1','symbol 2']}]
	@param capital: starting cash amount
	@param per_buy: per trade total amount, vol = per_buy/stock_price
	@param buy_cutoff: symbols[: cutoff * total sample number] -> buy these
	@param sell_cutoff: symbols[-1*cutoff * total sample number: ] -> sell these
	@param category: is the strategy ID

	@return: {date: asset value}
	@rtype: dict
	"""	
	def __init__(self,user,data,historicals,capital,per_buy,buy_cutoff,sell_cutoff,category):
		super(MySimulationAlpha,self).__init__(user,data,historicals,capital,per_buy,buy_cutoff,sell_cutoff,category)

	def sell(self, on_date, symbols):
		total_symbols = len(symbols)
		
		# sell if outside sell_cutoff
		positions = MyPosition.objects.filter(category = self.category, is_open = True).values_list("stock__symbol",flat=True).distinct()

		for symbol in symbols[-1*int(total_symbols*self.sell_cutoff):]:
			if symbol not in positions: continue # not an open position, next
			if symbol not in self.historicals[on_date]: continue # stock stopped trading?

			his = self.historicals[on_date][symbol]
			if 'adj_close' in his and his['adj_close'] > 0: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']

			pos = MyPosition.objects.get(stock__symbol=symbol,category = self.category, is_open=True)
			pos.close(self.user,simulated_spot,on_date=on_date)		

			self.capital += pos.vol * simulated_spot
			self.snapshot[on_date]['transaction']['sell'].append(pos)
			self.snapshot[on_date]['gain']['sell'] += pos.gain
			# print 'close: ',symbol,self.capital

	def buy(self, on_date, symbols):
		total_symbols = len(symbols)

		positions = MyPosition.objects.filter(category = self.category,is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols[:int(total_symbols*self.buy_cutoff)]:
			if symbol in positions: continue # already in portfolio, hold
			if self.capital < self.per_buy: continue # not enough fund
			if symbol not in self.historicals[on_date]: continue # stock stopped trading?

			# we buy, assuming knowing the ranking based on OPEN price
			# so we buy at CLOSE on that date
			his = self.historicals[on_date][symbol]
			if 'adj_close' in his and his['adj_close'] > 0: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']

			pos = MyPosition(
				stock = MyStock.objects.get(id=int(his['stock'])),
				user = self.user,
				position = simulated_spot, # buy
				vol = self.per_buy/simulated_spot,
				open_date = on_date,
				category = self.category,
				is_open = True)
			pos.save()

			self.capital -= pos.vol*pos.position
			self.snapshot[on_date]['transaction']['buy'].append(pos)		
			# print 'create: ',symbol, self.capital

class MySimulationJK(MySimulation):
	"""
	Trading strategy:

	1. Stocks are ranked by one-day change percentage. If pcnt < 0, price has dropped. The bigger the drop, the higher the rank.
	2. Buy stocks whose rank is above the buy_cutoff band, eg. if cutoff = 0.25 and total samples = 20, buy if rank <= 0.25*20=5
	3. Sell if stock's price has recovered more than sell_cutoff, eg. if cutoff = 0.25 and position @ 100, selll if new price >= 100*(1+0.25)

	@param user: request.user
	@param data: a list of dict, [{'on_date':date obj, 'ranks':['symbol 1','symbol 2']}]
	@param capital: starting cash amount
	@param per_buy: per trade total amount, vol = per_buy/stock_price
	@param buy_cutoff: daily_return < -1*buy_cutoff, buy
	@param sell_cutoff: price exit @ cost *(1+sell_cutoff)

	@return: {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets}
	@rtype: dict
	"""

	def __init__(self,user,data,historicals,capital,per_buy,buy_cutoff,sell_cutoff,category):
		super(MySimulationJK,self).__init__(user,data,historicals,capital,per_buy,buy_cutoff,sell_cutoff,category)

	def sell(self, on_date, symbols):
		total_symbols = len(symbols)

		# sell if outside sell_cutoff
		positions = MyPosition.objects.filter(category = self.category, is_open = True)
		for p in positions:
			# TODO: don't know why a symbol could stop showing up
			# in historicals. To protect such case, we put a line here.
			if p.stock.symbol not in self.historicals[on_date]: continue

			his = self.historicals[on_date][p.stock.symbol]
			simulated_spot = his['open_price'] # assume we are selling at open

			# for example, if sell_cutoff = 0.1, 
			# we sell if daily spot is greater than 110% of our cost
			if simulated_spot >= (1+self.sell_cutoff)*float(p.position):
				p.close(self.user,simulated_spot,on_date=on_date)

				self.capital += p.vol * simulated_spot
				self.snapshot[on_date]['transaction']['sell'].append(p)
				self.snapshot[on_date]['gain']['sell'] += p.gain
				# print 'close: ',symbol,self.capital

	def buy(self, on_date, symbols):
		total_symbols = len(symbols)

		# buy if within buy_cutoff	
		positions = MyPosition.objects.filter(category = self.category, is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols:
			# already in portfolio, hold
			if symbol in positions: continue

			# not enough fund
			if self.capital < self.per_buy: continue

			# if buy_cutoff = 0.04, 
			#   - if daily_return > -0.04, we skip
			#   - if one day drop greater than 4%, we buy
			his = self.historicals[on_date][symbol]
			daily_return = his['daily_return']
			if daily_return > -1*self.buy_cutoff: continue

			if 'adj_close' in his and his['adj_close'] > 0: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']

			pos = MyPosition(
				stock = MyStock.objects.get(id=int(his['stock'])),
				user = self.user,
				position = target_price, # buy
				vol = self.per_buy/simulated_spot,
				open_date = on_date,
				category = self.category)
			pos.save()

			self.capital -= pos.vol*pos.position
			self.snapshot[on_date]['transaction']['buy'].append(pos)		
			# print 'create: ',symbol, self.capital