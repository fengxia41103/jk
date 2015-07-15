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

class MyStockPrevYahoo():
	def __init__(self,handler):
		self.http_handler = handler
		self.agent = handler.agent
		self.logger = logging.getLogger('jk')

	def parser(self,symbol):
		# https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
		now = dt.now()
		a_week_ago = now-timedelta(7)

		date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d'%(now.month-1,now.day-1,now.year,a_week_ago.month-1,a_week_ago.day,a_week_ago.year)
		url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (symbol,date_str)
		self.logger.debug(url)
		content = self.http_handler.request(url)

		f = StringIO.StringIO(content)
		for vals in csv.reader(f)]:
			if len(vals) != 7: 
				self.logger.error('[%s] error, %d' % (symbol, len(vals)))
			else:
				stock = MyStock.objects.get(symbol=symbol)
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
