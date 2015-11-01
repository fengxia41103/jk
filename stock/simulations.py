from numpy import mean, std 
from collections import OrderedDict
from stock.models import *

def alpha_trading_simulation(user,data,historicals,capital,per_buy=1000,buy_cutoff=0.25,sell_cutoff=0.75,category=''):
	"""
	Trading strategy:

	1. Stocks are ranked by a pre-calculated index value
	2. Buy stocks whose rank is above the buy_cutoff band, eg. if buy_cutoff = 0.25 and total samples = 20, buy if rank <= 0.25*20=5
	3. Sell stocks when it falls out the sell_cutoff band, eg. if sell_cutoff = 0.75 and total samples = 20, sell if rank >= 0.75*20 = 15

	We simulate trades based on this strategy, then monitor the porfolio value (equity+cash).

	@param user: request.user
	@param data: a list of dict, [{'on_date':date obj, 'ranks':['symbol 1','symbol 2']}]
	@param capital: starting cash amount
	@param per_buy: per trade total amount, vol = per_buy/stock_price
	@param buy_cutoff: symbols[: cutoff * total sample number] -> buy these
	@param sell_cutoff: symbols[cutoff * total sample number: ] -> sell these

	@return: {date: asset value}
	@rtype: dict
	"""

	# clear all positions and reset porfolio cash
	MyPosition.objects.filter(category=category).delete()

	# asset simulation result
	assets = {}
	equity = {}
	cash = {}
	snapshot = OrderedDict()

	# trading
	for on_date,symbols_by_rank in data:
		print on_date.isoformat()
		positions = None		
		total_symbols = len(symbols_by_rank)

		# record transactions
		snapshot[on_date] = {
			'cash': 0,
			'equity': 0,
			'asset': 0,
			'portfolio':[],
			'transaction':{'buy':[],'sell':[]}, 
			'gain':{'hold':0,'sell':0}
		}

		# sell if outside sell_cutoff
		positions = MyPosition.objects.filter(category = category, is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols_by_rank[-1*int(total_symbols*sell_cutoff)-1:]:
			if symbol not in positions: continue # not an open position, next

			his = historicals[on_date][symbol]
			target_price = his['close_price'] # assuming we sell at close			
			pos = MyPosition.objects.get(stock__symbol=symbol,category = category, is_open=True)
			pos.close(user,target_price,on_date=on_date)			

			capital += pos.vol * target_price
			snapshot[on_date]['transaction']['sell'].append(pos)
			snapshot[on_date]['gain']['sell'] += pos.gain
			# print 'close: ',symbol,capital

		# buy if within buy_cutoff
		positions = MyPosition.objects.filter(category = category,is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols_by_rank[:int(total_symbols*buy_cutoff)]:
			if symbol in positions: continue # already in portfolio, hold
			if capital < per_buy: continue # not enough fund

			# we buy, assuming knowing the ranking based on OPEN price
			# so we buy at CLOSE on that date
			his = historicals[on_date][symbol]
			target_price = his['close_price'] # assuming we buy at close
			pos = MyPosition(
				stock = MyStock.objects.get(id=int(his['stock'])),
				user = user,
				position = target_price, # buy
				vol = per_buy/target_price,
				open_date = on_date,
				category = category,
				is_open = True)
			pos.save()

			capital -= pos.vol*pos.position
			snapshot[on_date]['transaction']['buy'].append(pos)
			# print 'create: ',symbol, capital

		# compute equity, cash, asset
		positions = MyPosition.objects.select_related().filter(category = category, is_open = True).values('stock__symbol','position','vol')
		temp = []
		for cnt,p in enumerate(positions):
			if p['stock__symbol'] in historicals[on_date]:
				# if symbol's historicals are missing for some reason
				# eg. stopped trading on that day, compay got bought
				# this would result some open position at the end of portfolio
				his = historicals[on_date][p['stock__symbol']]
			else: continue

			# we compute equity value based on daily close price
			if 'adj_close' in his: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']
			temp.append(p['vol'] * simulated_spot)
			snapshot[on_date]['gain']['hold'] += p['vol'] * (simulated_spot - p['position'])

		equity[on_date] = sum(temp)
		cash[on_date] = capital
		assets[on_date] = equity[on_date] + cash[on_date]
		
		snapshot[on_date]['cash'] = cash[on_date]
		snapshot[on_date]['equity'] = equity[on_date]
		snapshot[on_date]['asset'] = assets[on_date]
		snapshot[on_date]['portfolio'] = positions

	on_dates = [on_date for on_date,symbols in data]
	cashes = [float(cash[d]) for d in on_dates]
	equities = [float(equity[d]) for d in on_dates]
	assets = [float(assets[d]) for d in on_dates]

	return {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets, 'snapshots':snapshot}

def jk_trading_simulation(user,data,historicals,capital=100000,per_buy=1000,buy_cutoff=0.25,sell_cutoff=0.25,category=''):
	"""
	Trading strategy:

	1. Stocks are ranked by one-day change percentage. If pcnt < 0, price has dropped. The bigger the drop, the higher the rank.
	2. Buy stocks whose rank is above the buy_cutoff band, eg. if cutoff = 0.25 and total samples = 20, buy if rank <= 0.25*20=5
	3. Sell if stock's price has recovered more than sell_cutoff, eg. if cutoff = 0.25 and position @ 100, selll if new price >= 100*(1+0.25)

	@param user: request.user
	@param data: a list of dict, [{'on_date':date obj, 'ranks':['symbol 1','symbol 2']}]
	@param capital: starting cash amount
	@param per_buy: per trade total amount, vol = per_buy/stock_price
	@param buy_cutoff: oneday_change < -1*buy_cutoff, buy
	@param sell_cutoff: price exit @ cost *(1+sell_cutoff)

	@return: {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets}
	@rtype: dict
	"""

	# clear all positions and reset porfolio cash
	MyPosition.objects.filter(category = category).delete()

	# asset simulation result
	assets = {}
	equity = {}
	cash = {}
	transactions = {}
	positions = None

	# trading
	for on_date,symbols in data:
		print on_date.isoformat()

		# record transactions
		transactions[on_date] = {'buy':[],'sell':[]}

		# sell if meeting cutoff criteria
		positions = MyPosition.objects.filter(category = category, is_open = True)
		for p in positions:
			his = historicals[on_date][p.stock.symbol]
			simulated_spot = his['open_price'] # assume we are selling at open

			# for example, if sell_cutoff = 0.1, 
			# we sell if daily spot is greater than 110% of our cost
			if simulated_spot >= (1+sell_cutoff)*float(p.position):
				p.close(user,simulated_spot,on_date=on_date)
				capital += p.vol * simulated_spot
				transactions[on_date]['sell'].append(p)
				# print 'close: ',p.stock,capital

		# buy if within buy_cutoff	
		positions = MyPosition.objects.filter(category = category, is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols:
			# already in portfolio, hold
			if symbol in positions: continue

			# not enough fund
			if capital < per_buy: continue

			# if buy_cutoff = 0.04, 
			#   - if oneday_change > -0.04, we skip
			#   - if one day drop greater than 4%, we buy
			his = historicals[on_date][symbol]
			oneday_change = his['oneday_change']
			if oneday_change > -1*buy_cutoff: continue

			target_price = his['close_price'] # assuming we buy close
			pos = MyPosition(
				stock = MyStock.objects.get(id=int(his['stock'])),
				user = user,
				position = target_price, # buy
				vol = per_buy/target_price,
				open_date = on_date,
				category = category)
			pos.save()

			capital -= pos.vol*pos.position
			transactions[on_date]['buy'].append(pos)
			# print 'create: ',symbol, capital,target_price

		# compute equity, cash, asset
		positions = MyPosition.objects.select_related().filter(category = category, is_open = True).values('stock__symbol','vol')
		temp = []
		for p in positions:
			his = historicals[on_date][p['stock__symbol']]

			# we compute equity value based on daily close price
			if 'adj_close' in his: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']
			temp.append(p['vol'] * simulated_spot)

		equity[on_date] = sum(temp)
		cash[on_date] = capital
		assets[on_date] = equity[on_date] + cash[on_date]
		print cash[on_date], equity[on_date], assets[on_date]
		
	on_dates = [on_date for on_date,symbols in data]
	cashes = [float(cash[d]) for d in on_dates]
	equities = [float(equity[d]) for d in on_dates]
	assets = [float(assets[d]) for d in on_dates]

	return {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets, 'transactions':transactions}