import time
from numpy import mean, std
from collections import OrderedDict
import simplejson as json
from stock.models import *

class MySimulation(object):
	def __init__(self,user,simulation):
		self.trading_cost = 0.003 # 0.3% of buying amount
		self.user = user
		self.simulation = simulation
		self.data = []
		self.historicals = None
		self.snapshot = OrderedDict()
		self.capital = simulation.capital
		self.per_trade = simulation.per_trade
		self.buy_cutoff = simulation.buy_cutoff/100.0
		self.sell_cutoff = simulation.sell_cutoff/100.0

		# clear previous-run positions
		MyPosition.objects.filter(simulation=simulation).delete()

	def setup(self):
		index_val_mapping = {
			1:'daily_return',
			2:'relative_hl',
			3:'relative_ma',
			4:'cci',
			5:'si',
			6:'lg_slope',
			7:'decycler_oscillator'
		}

		# control variables
		start = self.simulation.start
		end = self.simulation.end
		strategy_value = self.simulation.strategy_value

		# sample set
		data_source = self.simulation.data_source
		sector = self.simulation.sector
		stocks = []		
		if data_source == 1:
			stocks = MyStock.objects.filter(is_sp500 = True).values_list('id', flat=True)
		elif data_source == 2:
			stocks = MyStock.objects.filter(symbol__startswith = "CI00").values_list('id', flat=True)			
		elif data_source == 3:
			stocks = MyStock.objects.filter(symbol__startswith = "8821").values_list('id', flat=True)
		elif data_source == 4:
			stocks = MyStock.objects.filter(is_china_stock = True).values_list('id', flat=True)
		elif data_source == 5 and sector:
			for s in MySector.objects.filter(code__startswith=sector):
				for stock in s.stocks.all():
					if stock.symbol.startswith('8821'): continue
					else: stocks.append(stock.id)		
		histories = MyStockHistorical.objects.select_related().filter(stock__in=stocks,date_stamp__range=[start,end]).values('stock','stock__symbol','date_stamp','open_price','close_price','adj_close','relative_hl','daily_return','val_by_strategy','relative_ma')

		# dates
		dates = list(set([h['date_stamp'] for h in histories]))
		dates.sort()
		start = dates[0]
		end = dates[-1]

		# reconstruct historicals by dates
		self.historicals = {}
		for h in histories:
			on_date = h['date_stamp']
			if on_date not in self.historicals: self.historicals[on_date]={}
			self.historicals[on_date][h['stock__symbol']] = h

		for on_date in dates:
			his_by_symbol = self.historicals[on_date]
			
			if self.simulation.strategy == 1:
				tmp = [(symbol,h[index_val_mapping[strategy_value]]) for symbol,h in his_by_symbol.iteritems()]			
				symbols_by_rank = [x[0] for x in sorted(tmp,key=lambda x: x[1],reverse=(self.simulation.data_sort == 1))] 				
				self.data.append((on_date,symbols_by_rank))
			elif self.simulation.strategy == 2:
				# for JK type trading, we don't need to sort		
				symbols = [symbol for symbol,h in his_by_symbol.iteritems()] 
				self.data.append((on_date,symbols))

	def run(self):
		# set up data points
		self.setup()

		# asset simulation result
		assets = {}
		equity = {}
		cash = {}
		
		# trading
		for on_date,symbols_by_rank in self.data:
			print self.simulation, on_date.isoformat()
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
			positions = MyPosition.objects.filter(simulation = self.simulation, is_open = True).values('stock__symbol','position','vol')
			temp = []
			for p in positions:
				if p['stock__symbol'] in self.historicals[on_date]:
					# if symbol's historicals are missing for some reason
					# eg. stopped trading on that day, compay got bought
					# this would result some open position at the end of portfolio
					his = self.historicals[on_date][p['stock__symbol']]

					# we compute equity value based on daily close price
					if 'adj_close' in his and his['adj_close'] > 0: simulated_spot = his['adj_close'] 
					elif 'close_price' in his and 'close_price' > 0: simulated_spot = his['close_price']
					else: simulated_spot = p['position'] # we don't have a close value, use cost
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
			self.snapshot[on_date]['portfolio'] = list(positions)

		on_dates = [on_date for on_date,symbols in self.data]
		cashes = [float(cash[d]) for d in on_dates]
		equities = [float(equity[d]) for d in on_dates]
		assets = [float(assets[d]) for d in on_dates]
		portfolios = [self.snapshot[d]['portfolio'] for d in on_dates]
		transactions = [self.snapshot[d]['transaction'] for d in on_dates]

		return {'on_dates':on_dates, 
			'cashes':cashes,
			'equities':equities,
			'assets':assets, 
			'portfolios': portfolios,
			'transactions': transactions,
			'snapshots':self.snapshot
		}

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
	"""	
	def __init__(self,user,simulation):
		super(MySimulationAlpha,self).__init__(user,simulation)

	def sell(self, on_date, symbols):
		total_symbols = len(symbols)

		# sell if outside sell_cutoff
		positions = MyPosition.objects.filter(simulation = self.simulation, is_open = True).values_list("stock__symbol",flat=True).distinct()

		# In this strategy, buy_cutoff defines the starting index, 
		# sell_cutoff defines the ending index. Everything outside this band is a sell.	
		start_cutoff = max(int(total_symbols*self.buy_cutoff)-1,0)
		end_cutoff = int(total_symbols*self.sell_cutoff)
		buys = symbols[start_cutoff:end_cutoff]
		sells = filter(lambda x: x not in buys, symbols)
		for symbol in sells:
			if symbol not in positions: 
				# print 'symbol not in positions'
				continue # not an open position, next
			if symbol not in self.historicals[on_date]: 
				# print 'symbol not in historical'
				continue # stock stopped trading?

			his = self.historicals[on_date][symbol]
			if 'adj_close' in his and his['adj_close'] > 0: simulated_spot = his['adj_close'] 
			elif 'close_price' in his and 'close_price' > 0: simulated_spot = his['close_price']

			pos = MyPosition.objects.get(stock__symbol=symbol,simulation = self.simulation, is_open=True)
			pos.close(self.user,simulated_spot,on_date=on_date)		

			self.capital += pos.vol * simulated_spot
			self.snapshot[on_date]['transaction']['sell'].append({
				'symbol':pos.stock.symbol,
				'position':pos.position,
				'close_position':pos.close_position,
				'gain':pos.gain,
				'life_in_days':pos.life_in_days,
				'vol':pos.vol
			})
			self.snapshot[on_date]['gain']['sell'] += pos.gain
			# print 'close: ',symbol,self.capital

	def buy(self, on_date, symbols):
		total_symbols = len(symbols)

		positions = MyPosition.objects.filter(simulation = self.simulation,is_open = True).values_list("stock__symbol",flat=True).distinct()

		# In this strategy, buy_cutoff defines the starting index, 
		# sell_cutoff defines the ending index. Everything within this band is a buy.
		start_cutoff = max(int(total_symbols*self.buy_cutoff)-1,0)
		end_cutoff = int(total_symbols*self.sell_cutoff)
		buys = symbols[start_cutoff:end_cutoff]
		sells = filter(lambda x: x not in buys, symbols)
		for symbol in buys:		
			if symbol in positions: continue # already in portfolio, hold
			if self.capital < self.per_trade: continue # not enough fund
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
				vol = self.per_trade/simulated_spot,
				open_date = on_date,
				simulation = self.simulation,
				is_open = True)
			pos.save()

			self.capital -= pos.vol*pos.position
			self.snapshot[on_date]['transaction']['buy'].append({
				'symbol': symbol,
				'position': simulated_spot,
				'vol': pos.vol
			})		
			# print 'create: ',symbol, self.capital

class MySimulationJK(MySimulation):
	"""
	Trading strategy:

	1. Stocks are ranked by one-day change percentage. If pcnt < 0, price has dropped. The bigger the drop, the higher the rank.
	2. Buy stocks whose rank is above the buy_cutoff band, eg. if cutoff = 0.25 and total samples = 20, buy if rank <= 0.25*20=5
	3. Sell if stock's price has recovered more than sell_cutoff, eg. if cutoff = 0.25 and position @ 100, selll if new price >= 100*(1+0.25)
	"""

	def __init__(self,user,simulation):
		super(MySimulationJK,self).__init__(user,simulation)

	def sell(self, on_date, symbols):
		total_symbols = len(symbols)

		# sell if outside sell_cutoff
		positions = MyPosition.objects.filter(simulation = self.simulation, is_open = True)
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
				self.snapshot[on_date]['transaction']['sell'].append({
					'symbol':p.stock.symbol,
					'position':p.position,
					'close_position':p.close_position,
					'gain':p.gain,
					'life_in_days':p.life_in_days,
					'vol':p.vol
				})
				self.snapshot[on_date]['gain']['sell'] += p.gain
				# print 'close: ',symbol,self.capital

	def buy(self, on_date, symbols):
		total_symbols = len(symbols)

		# buy if within buy_cutoff	
		positions = MyPosition.objects.filter(simulation = self.simulation, is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols:
			# already in portfolio, hold
			if symbol in positions: continue

			# not enough fund
			if self.capital < self.per_trade: continue

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
				position = simulated_spot, # buy
				vol = self.per_trade/simulated_spot,
				open_date = on_date,
				simulation = self.simulation)
			pos.save()

			self.capital -= pos.vol*pos.position
			self.snapshot[on_date]['transaction']['buy'].append({
				'symbol': symbol,
				'position': simulated_spot,
				'vol': pos.vol
			})	
			# print 'create: ',symbol, self.capital