# -*- coding: utf-8 -*- 
from __future__ import absolute_import

from celery import shared_task

import lxml.html
import simplejson as json
import pytz
import logging
from random import randint
import time
import hashlib
import urllib, urllib2
from tempfile import NamedTemporaryFile
from django.core.files import File
import codecs
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re
from datetime import timedelta
import datetime as dt
from itertools import izip_longest
from lxml.html.clean import clean_html

from jk.tor_handler import *
from stock.models import *

# create logger with 'spam_application'
logger = logging.getLogger('jk')
logger.setLevel(logging.DEBUG)

def grouper(iterable, n, padvalue=None):
	# grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')
	return list(izip_longest(*[iter(iterable)]*n, fillvalue=padvalue))

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from random import shuffle
from decimal import Decimal
import csv, StringIO
from dateutil.relativedelta import relativedelta

class MyStockFlagSP500():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self):
		# clear is_sp500 flag
		for s in MyStock.objects.all():
			s.is_sp500 = False
			s.save()

		url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv'
		content = self.http_handler.request(url)
		# self.logger.debug(content)

		f = StringIO.StringIO(content)
		for index,vals in enumerate(csv.reader(f)):
			if not index: continue
			if len(vals) != 3: 
				self.logger.error('[%s] error, %d' % (vals[0], len(vals)))
				continue

			stock,created = MyStock.objects.get_or_create(symbol=vals[0])
			stock.is_sp500 = True
			stock.sector = vals[-1]
			stock.save()
			self.logger.debug('[%s] complete'%vals[0])

@shared_task
def stock_flag_sp500_consumer():
	http_agent = PlainUtility()
	crawler = MyStockFlagSP500(http_agent)
	crawler.parser()

class MyStockPrevYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		# https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
		now = dt.now()
		ago = now-timedelta(7)

		date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d'%(now.month-1,now.day,now.year,ago.month-1,ago.day,ago.year)
		url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (symbol,date_str)
		self.logger.debug(url)
		content = self.http_handler.request(url)

		stock = MyStock.objects.get(symbol=symbol)
		f = StringIO.StringIO(content)
		for vals in csv.reader(f):
			if len(vals) != 7:
				self.logger.error('[%s] error, %d' % (symbol, len(vals)))
			elif 'Open' in vals[1]: continue # title line
			else: 
				stock.prev_open = Decimal(vals[1])
				stock.prev_high = Decimal(vals[2])
				stock.prev_low = Decimal(vals[3])
				stock.prev_close = Decimal(vals[4])
				stock.prev_change = (stock.prev_open-stock.prev_close)/stock.prev_open*Decimal(100.0)
				stock.save()
				self.logger.debug('[%s] complete'%symbol)
				break

@shared_task
def stock_prev_yahoo_consumer(symbol):
	http_agent = PlainUtility()
	crawler = MyStockPrevYahoo(http_agent)
	crawler.parser(symbol)

class MyStockPrevWeekYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		# https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
		now = dt.now()
		ago = now-timedelta(weeks=1)

		date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d'%(ago.month-1,ago.day,ago.year,now.month-1,now.day,now.year)
		url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (symbol,date_str)
		self.logger.debug(url)
		content = self.http_handler.request(url)

		stock = MyStock.objects.get(symbol=symbol)
		adj_close = []
		f = StringIO.StringIO(content)
		cnt = 0
		for vals in csv.reader(f):
			if len(vals) != 7: 
				self.logger.error('[%s] error, %d' % (symbol, len(vals)))
			elif 'Adj' in vals[-1]: continue
			elif cnt < 7: 
				adj_close.append(vals[-1])
				cnt+=1
			elif cnt >= 7: break

		# persist
		stock.week_adjusted_close = ','.join(list(reversed(adj_close)))
		stock.save()
		self.logger.debug('[%s] complete'%symbol)

@shared_task
def stock_prev_week_yahoo_consumer(symbol):
	http_agent = PlainUtility()
	crawler = MyStockPrevWeekYahoo(http_agent)
	crawler.parser(symbol)

class MyStockPrevMonthYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		# https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
		now = dt.now()
		ago = now+relativedelta(months=-1)

		date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d'%(ago.month-1,ago.day,ago.year,now.month-1,now.day,now.year)
		url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=w&ignore=.csv' % (symbol,date_str)
		self.logger.debug(url)
		content = self.http_handler.request(url)

		stock = MyStock.objects.get(symbol=symbol)
		adj_close = []
		f = StringIO.StringIO(content)
		cnt = 0
		for vals in csv.reader(f):
			if len(vals) != 7: 
				self.logger.error('[%s] error, %d' % (symbol, len(vals)))
			elif 'Adj' in vals[-1]: continue
			elif cnt < 4: 
				adj_close.append(vals[-1])
				cnt += 1
			elif cnt >= 4: break

		# persist
		stock.month_adjusted_close = ','.join(list(reversed(adj_close)))
		stock.save()
		self.logger.debug('[%s] complete'%symbol)

@shared_task
def stock_prev_month_yahoo_consumer(symbol):
	http_agent = PlainUtility()
	crawler = MyStockPrevMonthYahoo(http_agent)
	crawler.parser(symbol)

class MyStockPrevFibYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		stock = MyStock.objects.get(symbol=symbol)
		fib = [5,8,13,21,34,55,89,144,233,377]
		fib_ratio = [a/100 for a in [0.0, 23.6, 38.2, 50, 61.8, 100, 161.8, 261.8, 423.6]]

		# https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
		now = dt.now()
		ago = now+relativedelta(months=-180)

		date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d'%(ago.month-1,ago.day,ago.year,now.month-1,now.day,now.year)
		for interval in ['w','d']:		
			url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=%s&ignore=.csv' % (symbol,date_str,interval)
			self.logger.debug(url)
			content = self.http_handler.request(url)
			adj_close = []

			f = StringIO.StringIO(content)
			for cnt, vals in enumerate(csv.reader(f)):
				if len(vals) != 7: 
					self.logger.error('[%s] error, %d' % (symbol, len(vals)))
				elif 'Adj' in vals[-1]: continue
				elif cnt in fib: 
					adj_close.append(vals[-1])
				elif cnt > fib[-1]: break # no more need

			# compute diff = T(n+1)-T(n)
			adj_close = list(reversed(adj_close))
			tmp = [float(a) for a in adj_close]
			tmp = [a-b for a,b in zip(tmp[1:],tmp)]
			# persist
			if interval == 'w': 
				stock.fib_weekly_adjusted_close = ','.join(adj_close)

				stock.fib_weekly_score = sum([a*b for a,b in zip(tmp,fib_ratio)])
			elif interval == 'd': 
				stock.fib_daily_adjusted_close = ','.join(adj_close)
				stock.fib_daily_score = sum([a*b for a,b in zip(tmp,fib_ratio)])

			stock.save()
		self.logger.debug('[%s] complete'%symbol)

@shared_task
def stock_prev_fib_yahoo_consumer(symbol):
	http_agent = PlainUtility()
	crawler = MyStockPrevFibYahoo(http_agent)
	crawler.parser(symbol)		

class MyStockHistoricalYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		stock = MyStock.objects.get(symbol=symbol)
		his = [x.isoformat() for x in MyStockHistorical.objects.filter(stock=stock).values_list('date_stamp',flat=True)]

		# https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
		now = dt.now()
		ago = now+relativedelta(months=-180) # 180 months = 15 yrs

		date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d'%(ago.month-1,ago.day,ago.year,now.month-1,now.day,now.year)	
		url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (symbol,date_str)
		self.logger.debug(url)
		content = self.http_handler.request(url)

		f = StringIO.StringIO(content)
		records = []
		for cnt, vals in enumerate(csv.reader(f)):
			if not vals: continue # protect from blank line or invalid symbol, eg. China stock symbols
			elif not reduce(lambda x,y: x and y, vals): continue # any empty string, None will be skipped
			elif len(vals) != 7: 
				self.logger.error('[%s] error, %d' % (symbol, len(vals)))
				continue
			elif 'Adj' in vals[-1]: continue

			stamp = [int(v) for v in vals[0].split('-')]
			date_stamp = dt(year=stamp[0],month=stamp[1],day=stamp[2])
			# # exist = MyStockHistorical.objects.filter(stock=stock,date_stamp=date_stamp)

			# if len(exist): continue
			if date_stamp.date().isoformat() in his: continue # we already have these
			else:
				try: open_p=Decimal(vals[1])
				except: open_p=Decimal(-1)
				try: high_p=Decimal(vals[2])
				except: high_p=Decimal(-1)		
				try: low_p=Decimal(vals[3])
				except: low_p=Decimal(-1)
				try: close_p=Decimal(vals[4])
				except: close_p=Decimal(-1)
				try: vol=int(vals[5])/1000.0
				except: vol=-1
				try: adj_p=Decimal(vals[6])
				except: adj_p=Decimal(-1)				
				h = MyStockHistorical(
						stock=stock,
						date_stamp=date_stamp,
						open_price=open_p,
						high_price=high_p,
						low_price=low_p,
						close_price=close_p,
						vol=vol,
						adj_close=adj_p
					)
				records.append(h)
				if len(records) >= 1000:
					MyStockHistorical.objects.bulk_create(records)
					records = []
		# persist
		self.logger.debug('[%s] complete'%symbol)

@shared_task
def stock_historical_yahoo_consumer(symbol):
	http_agent = PlainUtility()
	crawler = MyStockHistoricalYahoo(http_agent)
	crawler.parser(symbol)	

class MyStockMonitorYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbols):
		# https://greenido.wordpress.com/2009/12/22/yahoo-finance-hidden-api/
		url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=srpoabvf6ml1n'%symbols
		content = self.http_handler.request(url)
		# self.logger.debug(content)

		f = StringIO.StringIO(content)
		for vals in csv.reader(f):
			if len(vals) != 11: 
				self.logger.error('[%s] error, %d' % (vals[0], len(vals)))
				continue

			stock = MyStock.objects.get(symbol=vals[0])
			try: stock.pe = Decimal(vals[1])
			except: pass

			stock.day_open = Decimal(vals[3])
			
			try: stock.ask = Decimal(vals[4])
			except: pass
			try: stock.bid = Decimal(vals[5])
			except: pass

			stock.vol = int(vals[6])/1000.0
			
			try: stock.float_share = float(vals[7])/1000000
			except: pass # could bve N/A

			if '-' in vals[8]:
				stock.day_low = Decimal(vals[8].split('-')[0])
				stock.day_high = Decimal(vals[8].split('-')[1])

			stock.last = Decimal(vals[9])
			stock.company_name = vals[10]
			stock.save()
			self.logger.debug('[%s] complete'%vals[0])

@shared_task
def stock_monitor_yahoo_consumer(symbols):
	http_agent = PlainUtility()
	crawler = MyStockMonitorYahoo(http_agent)
	crawler.parser(symbols)	

class MyStockMonitorYahoo2():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbols):
		url = 'http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json&view=detail' % symbols
		content = self.http_handler.request(url)
		content = json.loads(content)
		for r in content['list']['resources']:
			fields = r['resource']['fields']
			symbol = fields['symbol']
			stock = MyStock.objects.get(symbol=symbol)
			stock.last = Decimal(fields['price'])

			# last update time
			stock.save()
			self.logger.debug('[%s] complete'%symbol)

@shared_task
def stock_monitor_yahoo_consumer2(symbols):
	http_agent = PlainUtility()
	crawler = MyStockMonitorYahoo2(http_agent)
	crawler.parser(symbols)

import xlrd,xlwt,os,os.path
class MyChenMin():
	def __init__(self):
		self.logger = logging.getLogger('jk')		

	def parser(self,f,output=None):
		try: book = xlrd.open_workbook(f)
		except:
			self.logger.error('%s error' % f)
			return

		sh = book.sheet_by_index(0)
		if sh.name != u'账户对账单': self.logger.error(f)

		# range for 账户对账单
		first_col_vals = [sh.cell_value(rowx=i, colx=0) for i in range(sh.nrows)]
		start=end=None
		for idx, val in enumerate(first_col_vals):
			if val == u'对帐单': start=idx
			if val == u'当日持仓清单': end = idx
			if start and end: break

		vals = []
		for row in xrange(start,end):
			vals.append([sh.cell_value(rowx=row,colx=c) for c in range(sh.ncols)])

		for row in filter(lambda x: u'20' in x[0], vals):
			symbol = row[3]
			transaction_type = row[1]
			price = float(row[7])
			vol = int(row[5])
			total = float(row[8])
			name = row[4]

			# timestamp
			yr = int(row[0][:4])
			m = int(row[0][5:6])
			d = int(row[0][-2:])
			executed_on = dt(year=yr,month=m,day=d)

			c = MyChenmin(
				executed_on = executed_on,
				transaction_type = transaction_type,
				symbol=symbol,
				name=name,
				price=price,
				vol=vol,
				total=total
				)
			c.save()
		self.logger.debug('%s done'%f)

@shared_task
def chenmin_consumer(files):
	crawler = MyChenMin()
	crawler.parser(files)

from influxdb.influxdb08 import InfluxDBClient
import time
class MyStockInflux():
	def __init__(self):
		self.logger = logging.getLogger('jk')

		db_name = 'stock'
		self.client = InfluxDBClient('localhost', 8086, 'root', 'root', db_name)		
		# all_dbs_list = self.client.get_list_database()
		# that list comes back like: [{u'name': u'hello_world'}]
		# if db_name not in [str(x['name']) for x in all_dbs_list]:
		# 	print "Creating db {0}".format(db_name)
		# 	self.client.create_database(db_name)
		# else:
		# 	print "Reusing db {0}".format(db_name)
		self.client.switch_db(db_name)	

	def parser(self,symbol):
		points = []
		for h in MyStockHistorical.objects.filter(stock__symbol=symbol).order_by('date_stamp'):
			points=[[h.id,h.date_stamp.strftime('%Y-%m-%d'),time.mktime(h.date_stamp.timetuple()),float(h.open_price),float(h.high_price),float(h.low_price),float(h.close_price),float(h.adj_close),h.vol]]

			self.client.write_points([{
				'name':symbol,
				'columns':['id','date','time','open','high','low','close','adj_close','vol'],
				'points':points
				}], time_precision='s')

		self.logger.debug('%s completed'%symbol)

@shared_task
def influx_consumer(symbol):
	crawler = MyStockInflux()
	crawler.parser(symbol)

class MyStockBacktesting_1():
	def __init__(self):
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		self.logger.debug('%s starting' % symbol)
		exec_start = time.time()

		records = MyStockHistorical.objects.filter(stock__symbol=symbol).order_by('date_stamp')

		# The starting point is depending on how much past data your strategy is calling for.
		# For example, if we are to calculate 10 weeks of fib score, we need at least 10 weeks of history data.
		start = 10
		if start > len(records):
			self.logger.error('%s: not enough data'%symbol)
			return

		t0 = None
		for i in range(start,len(records)):
			self.logger.debug('%s: %d/%d' % (symbol, i,len(records)))
			prev_d = records[i-1]
			t0 =  records[i] # set T0
			now = t0.date_stamp

			# day changes
			spot = float(t0.high_price+t0.low_price)/2.0 # simulate a middle point between high and low as spot
			oneday_change = (spot-float(t0.open_price))/float(t0.open_price)*100.0
			twoday_change = (spot-float(prev_d.open_price))/float(prev_d.open_price)*100.0

			# week changes
			ago = now+relativedelta(days=-5) # search for last week's
			prev_week = records.filter(stock=t0.stock,date_stamp = ago)
			if prev_week: prev_week=prev_week[0]
			else: continue # not enough data points for this strategy
			week_change = (spot - float(prev_week.open_price))/float(prev_week.open_price)*100.0

			# month changes
			ago = now+relativedelta(months=-1) # search for last month's
			prev_mon = records.filter(stock=t0.stock,date_stamp = ago)
			if prev_mon: prev_mon = prev_mon[0]
			else: continue # not enough data points for this strategy
			month_change = (spot - float(prev_mon.open_price))/float(prev_mon.open_price)*100.0

			# consistency
			if oneday_change>0 and twoday_change>0 and week_change>0 and month_change>0:
				trend_is_consistent_gain = True
			else: trend_is_consistent_gain = False

			if oneday_change<0 and twoday_change<0 and week_change<0 and month_change<0:
				trend_is_consistent_loss = True
			else: trend_is_consistent_loss = False

			"""
			Strategy: marked as "G" if trend is consistently gaining, "L" if consistently losing, "U" if otherwise.
			"""
			if trend_is_consistent_gain: t0.flag_by_strategy = 'G' # "gain"
			elif trend_is_consistent_loss: t0.flag_by_strategy = 'L' # "loss"
			else: t0.flag_by_strategy = 'U' # stands for "unknown"
			
			# save to DB
			t0.save()

		self.logger.debug('%s completed, elapse %f'%(symbol, time.time()-exec_start))

@shared_task
def backtesting_s1_consumer(symbol):
	crawler = MyStockBacktesting_1()
	crawler.parser(symbol)

from numpy import mean, std 
class MyStockBacktesting_2():
	"""
	This strategy is based on Chenmin's email:

	交易思想如下，根据某指标，对每只指数进行排名，排入前25%的，就进行持仓； 一旦持仓，落后到40%以后，则平仓出来。。
	比如，在9/12,  CI005025 排名从第10跳到第6， 则LONG之（第6名相当于 6/29 =20% ） ；  到9/19, 排名第一次跌出前 12名； 则平仓。。

	为了对冲做多的风险，对应地也对这些指数进行做空，一样，排名后25%， 则做空，返回到 60%以内，则平仓。。

	下面只剩下指标怎么定义： 
	采用以下进行测试：
	指标 = ( 价格- （N日均价))/N日价格的标准差     指标值越大，则排名越靠前	

	N = int(M/4), where M is the total number of stocks participating in ranks	
	"""
	def __init__(self):
		self.logger = logging.getLogger('jk')

	def parser(self, symbol, window_length=7):
		self.logger.debug('%s starting' % symbol)
		exec_start = time.time()

		records = MyStockHistorical.objects.filter(stock__symbol=symbol).order_by('date_stamp')
		start = window_length
		if window_length > len(records):
			self.logger.error('%s: not enough data'%symbol)
			return

		t0 = prev = None
		for i in range(window_length,len(records)):
			self.logger.debug('%s: %d/%d' % (symbol, i,len(records)))
			window = records[i-window_length:i]
			t0 =  records[i] # set T0
			prev = records[i-1] # set to T-1
			
			# compute index value
			# data = map(lambda x: mean([x.high_price,x.low_price]), window)
			# window_avg = mean(data)
			# window_std = std(data)
			# t0.val_by_strategy = (t0.open_price-window_avg)/window_std
			t0.val_by_strategy = (t0.close_price-prev.close_price)/prev.close_price*100

			# save to DB
			t0.save()

		self.logger.debug('%s completed, elapse %f'%(symbol, time.time()-exec_start))

@shared_task
def backtesting_s2_consumer(symbol):
	crawler = MyStockBacktesting_2()
	crawler.parser(symbol)

class MyStockBacktesting_2_rank():
	"""
	Based on the score calculated by strategy 2, we rank all stocks per date
	"""
	def __init__(self):
		self.logger = logging.getLogger('jk')

	def parser(self, on_date, ascending=True):
		self.logger.debug('%s starting' % on_date.isoformat())
		exec_start = time.time()

		if ascending:
			his = MyStockHistorical.objects.filter(stock__symbol__startswith="CI00", date_stamp = on_date).order_by('val_by_strategy')
		else:
			his = MyStockHistorical.objects.filter(stock__symbol__startswith="CI00", date_stamp = on_date).order_by('-val_by_strategy')			
		for i in range(len(his)):
			his[i].peer_rank = i
			his[i].save()

		self.logger.debug('%s completed, elapse %f'%(on_date.isoformat(), time.time()-exec_start))

@shared_task
def backtesting_s2_rank_consumer(on_date,ascending):
	crawler = MyStockBacktesting_2_rank()
	crawler.parser(dt.strptime(on_date, "%Y-%m-%d").date(),ascending)

class MyStockBacktesting_3():
	"""
	For a SP500 stock, we rank them by daily price change (t0's open vs. t-1's close),
	a negative price change would mean the stock price dropped badly on T0 -> we buy it.
	When its daily change is positive and ranked high, we sell.

	Scenario #1: it had a steep drop but never a steep rise -> we will be holding this stock for a long time;
	Scenario #2: 
	"""	
	def __init__(self):
		self.logger = logging.getLogger('jk')

	def parser(self,symbol,window_length=2):
		self.logger.debug('%s starting' % symbol)
		exec_start = time.time()

		records = MyStockHistorical.objects.filter(stock__symbol=symbol).order_by('date_stamp')

		# The starting point is depending on how much past data your strategy is calling for.
		# For example, if we are to calculate 10 weeks of fib score, we need at least 10 weeks of history data.
		if window_length > len(records):
			self.logger.error('%s: not enough data'%symbol)
			return

		t0 = ''
		for i in range(window_length,len(records)):
			self.logger.debug('%s: %d/%d' % (symbol, i,len(records)))
			window = records[i-window_length:i]
			t0 =  records[i] # set T0
			prev = records[i-1] # set T-1

			# compute index value
			if prev.adj_close and prev.adj_close > 0:
				t0.val_by_strategy = (t0.close_price - prev.adj_close)/prev.adj_close*100
				t0.oneday_change = (t0.close_price - prev.adj_close)/prev.adj_close*100
			elif prev.close_price and prev.close_price > 0:
				t0.val_by_strategy = (t0.close_price - prev.close_price)/prev.close_price*100
				t0.oneday_change = (t0.close_price - prev.close_price)/prev.close_price*100
			# save to DB
			t0.save()

		self.logger.debug('%s completed, elapse %f'%(symbol, time.time()-exec_start))

@shared_task
def backtesting_s3_consumer(symbol):
	crawler = MyStockBacktesting_3()
	crawler.parser(symbol)

class MyStockBacktesting_3_rank():
	"""
	Based on the score calculated by strategy 3, we rank all stocks per date
	"""
	def __init__(self):
		self.logger = logging.getLogger('jk')

	def parser(self, on_date):
		self.logger.debug('%s starting' % on_date.isoformat())
		exec_start = time.time()

		his = MyStockHistorical.objects.filter(stock__is_sp500 = True, date_stamp = on_date).order_by('-val_by_strategy')
		for i in range(len(his)):
			his[i].peer_rank = i
			his[i].save()

		self.logger.debug('%s completed, elapse %f'%(on_date.isoformat(), time.time()-exec_start))

@shared_task
def backtesting_s3_rank_consumer(on_date):
	crawler = MyStockBacktesting_3_rank()
	crawler.parser(dt.strptime(on_date, "%Y-%m-%d").date())	