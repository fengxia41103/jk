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

			# persist
			if interval == 'w': stock.fib_weekly_adjusted_close = ','.join(list(reversed(adj_close)))
			elif interval == 'd': stock.fib_daily_adjusted_close = ','.join(list(reversed(adj_close)))
			stock.save()
		self.logger.debug('[%s] complete'%symbol)

@shared_task
def stock_prev_fib_yahoo_consumer(symbol):
	http_agent = PlainUtility()
	crawler = MyStockPrevFibYahoo(http_agent)
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