from numpy import mean, std 
from stock.models import *


def alpha_trading_simulation(user,data,historicals,capital=100000,per_buy=1000,buy_cutoff=0.25,sell_cutoff=0.75,category=''):
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
	positions = None
	
	# trading
	for on_date,symbols_by_rank in data:
		print on_date.isoformat()
		total_symbols = len(symbols_by_rank)

		# sell if outside sell_cutoff
		positions = MyPosition.objects.filter(category = category, is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols_by_rank[int(total_symbols*sell_cutoff):]:
			if symbol not in positions: continue # not an open position, next

			his = historicals[on_date][symbol]
			target_price = his['low_price'] # assuming we sell at daily low				
			pos = MyPosition.objects.get(stock__symbol=symbol,category = category, is_open=True)
			pos.close(user,target_price,on_date=on_date)

			capital += pos.vol * target_price
			print 'close: ',symbol,capital

		# buy if within buy_cutoff
		positions = MyPosition.objects.filter(category = category,is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols_by_rank[:int(total_symbols*buy_cutoff)]:
			if symbol in positions: continue # already in portfolio, hold
			if capital < per_buy: continue # not enough fund

			# we buy, assuming knowing the ranking based on OPEN price
			# so we buy at mean(high,low) on that date
			his = historicals[on_date][symbol]
			target_price = mean([his['high_price'],his['low_price']]) # assuming we buy at daily avg
			pos = MyPosition(
				stock = MyStock.objects.get(id=int(his['stock'])),
				user = user,
				position = target_price, # buy
				vol = per_buy/target_price,
				open_date = on_date,
				category = category)
			pos.save()

			capital -= pos.vol*pos.position
			print 'create: ',symbol, capital

		# compute equity, cash, asset
		positions = MyPosition.objects.select_related().filter(category = category, is_open = True).values('stock__symbol','vol')
		temp = []
		for p in positions:
			his = historicals[on_date][p['stock__symbol']]

			# we compute equity value based on daily close price
			if 'adj_close' in his: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']
			elif 'high_price' in his and 'low_price' in his: simulated_spot = mean([his['high_price'],his['low_price']])
			temp.append(p['vol'] * simulated_spot)

		equity[on_date] = sum(temp)
		cash[on_date] = capital
		assets[on_date] = equity[on_date] + cash[on_date]
		print cash[on_date], equity[on_date], assets[on_date]
		
	on_dates = [on_date for on_date,symbols in data]
	cashes = [float(cash[d]) for d in on_dates]
	equities = [float(equity[d]) for d in on_dates]
	assets = [float(assets[d]) for d in on_dates]

	return {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets}

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
	@param buy_cutoff: symbols[: cutoff * total sample number] -> buy these
	@param sell_cutoff: price exit @ position price *(1+sell_cutoff)

	@return: {date: asset value}
	@rtype: dict
	"""

	# clear all positions and reset porfolio cash
	MyPosition.objects.filter(category = category).delete()

	# asset simulation result
	assets = {}
	equity = {}
	cash = {}
	positions = None

	# trading
	for on_date,symbols in data:
		print on_date.isoformat()

		# sell if meeting cutoff criteria
		positions = MyPosition.objects.filter(category = category, is_open = True)
		for p in positions:
			his = historicals[on_date][p.stock.symbol]
			simulated_spot = mean([his['high_price'],his['low_price']])

			# if sell_cutoff = 0.1, 
			# we sell if daily spot is greater than 110% of our cost
			if simulated_spot >= (1+sell_cutoff)*float(p.position):
				p.close(user,simulated_spot,on_date=on_date)
				capital += p.vol * simulated_spot
				print 'close: ',p.stock,capital

		# buy if within buy_cutoff	
		positions = MyPosition.objects.filter(category = category, is_open = True).values_list("stock__symbol",flat=True).distinct()
		for symbol in symbols:
			# already in portfolio, hold
			if symbol in positions: continue

			# not enough fund
			if capital < per_buy: continue

			# if buy_cutoff = 0.04, 
			#   - if oneday_change_pcnt > -0.04, we skip
			#   - if one day drop greater than 4%, we buy
			his = historicals[on_date][symbol]
			oneday_change_pcnt = his['oneday_change_pcnt']
			if oneday_change_pcnt > -1*buy_cutoff: continue

			target_price = mean([his['high_price'],his['low_price']]) # assuming we buy at daily mean
			pos = MyPosition(
				stock = MyStock.objects.get(id=int(his['stock'])),
				user = user,
				position = target_price, # buy
				vol = per_buy/target_price,
				open_date = on_date,
				category = category)
			pos.save()

			capital -= pos.vol*pos.position
			print 'create: ',symbol, capital,target_price

		# compute equity, cash, asset
		positions = MyPosition.objects.select_related().filter(category = category, is_open = True).values('stock__symbol','vol')
		temp = []
		for p in positions:
			his = historicals[on_date][p['stock__symbol']]

			# we compute equity value based on daily close price
			if 'adj_close' in his: simulated_spot = his['adj_close'] 
			elif 'close_price' in his: simulated_spot = his['close_price']
			elif 'high_price' in his and 'low_price' in his: simulated_spot = mean([his['high_price'],his['low_price']])
			temp.append(p['vol'] * simulated_spot)

		equity[on_date] = sum(temp)
		cash[on_date] = capital
		assets[on_date] = equity[on_date] + cash[on_date]
		print cash[on_date], equity[on_date], assets[on_date]
		
	on_dates = [on_date for on_date,symbols in data]
	cashes = [float(cash[d]) for d in on_dates]
	equities = [float(equity[d]) for d in on_dates]
	assets = [float(assets[d]) for d in on_dates]

	return {'on_dates':on_dates, 'cashes':cashes,'equities':equities, 'assets':assets}