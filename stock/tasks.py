# -*- coding: utf-8 -*-
from __future__ import absolute_import

import codecs
import cPickle
import csv
import datetime as dt
import hashlib
import logging
import os
import os.path
import re
import StringIO
import sys
import time
import urllib
import urllib2
from datetime import timedelta
from decimal import Decimal
from itertools import izip_longest
from math import cos
from math import sin
from random import randint
from random import shuffle
from tempfile import NamedTemporaryFile

import lxml.html
import numpy as np
import pytz
import simplejson as json
import xlrd
import xlwt
from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.files import File
from influxdb.influxdb08 import InfluxDBClient
from lxml.html.clean import clean_html
from numpy import mean
from numpy import std
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import \
    WebDriverWait  # available since 2.4.0

from jk.production_envvars import ALPHAVANTAGE_KEY
from jk.tor_handler import *
from scipy import stats
from stock.models import *
from stock.simulations import *

logger = logging.getLogger('jk')


def grouper(iterable, n, padvalue=None):
    # grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'),
    # ('g','x','x')
    return list(izip_longest(*[iter(iterable)] * n, fillvalue=padvalue))


class MyStockFlagSP500():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self):
        # clear is_sp500 flag
        for s in MyStock.objects.all():
            s.is_sp500 = False
            s.save()

        url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv'
        content = self.http_handler.request(url)
        # logger.debug(content)

        f = StringIO.StringIO(content)
        for index, vals in enumerate(csv.reader(f)):
            if not index:
                continue
            if len(vals) != 3:
                logger.error('[%s] error, %d' % (vals[0], len(vals)))
                continue

            stock, created = MyStock.objects.get_or_create(symbol=vals[0])
            stock.company_name = vals[1]
            stock.is_sp500 = True
            stock.sector = vals[-1]
            stock.save()
            logger.debug('[%s] complete' % vals[0])


@shared_task
def stock_flag_sp500_consumer():
    http_agent = PlainUtility()
    crawler = MyStockFlagSP500(http_agent)
    crawler.parser()


class MyStockBacktestingSimulation():

    def __init__(self, condition):
        # Model MySimulation is not json-able,
        # so we are passing it over as python pickle, so cool!
        self.condition = cPickle.loads(str(condition))

    def run(self, is_update):
        """Simulation run.

        Arguments:
            :is_update: True if we are to remove existing
                    simulation results and run simulation from
                    scratch; False will exit if there are existing
                    results already so we don't run the same
                    simulation twice.
        """
        # pick a user
        user = User.objects.all()[0]

        # simulate
        existing_results = MySimulationSnapshot.objects.filter(
            simulation=self.condition)
        if is_update:
            existing_results.delete()
        elif len(existing_results):
            return

        logger.debug('%s simulation starting' % self.condition)

        # simulate tradings
        exec_start = time.time()
        simulation_methods = {
            1: 'MySimulationAlpha',
            2: 'MySimulationJK'
        }
        trading_method = getattr(sys.modules[__name__], simulation_methods[
                                 self.condition.strategy])
        simulator = trading_method(user, simulation=self.condition)
        simulator.run()

        logger.debug(' %s simulation end %f' %
                     (self.condition, time.time() - exec_start))


@shared_task
def backtesting_simulation_consumer(condition, is_update=False):
    crawler = MyStockBacktestingSimulation(condition)
    crawler.run(is_update)


class MyStockHistoricalAlphaVantage():
    """Read historical daily from Alpha Vantage API.

    There are two versions: daily and adjusted. On most days they are the same,
    but we are sving them separately.

    API doc: https://www.alphavantage.co/documentation/
    """

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        stock = MyStock.objects.get(symbol=symbol)
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=%s&outputsize=full&apikey=%s' % (
            symbol, ALPHAVANTAGE_KEY)
        daily = self.http_handler.request(url)
        daily = json.loads(daily)
        logger.debug('[%s]:  reading daily historicals' % symbol)

        existing = MyStockHistorical.objects.filter(stock=stock)
        to_save = {}
        for day, details in daily['Time Series (Daily)'].items():
            ds = day.split('-')
            date_stamp = dt(year=int(ds[0]), month=int(ds[1]), day=int(ds[2]))
            aa = existing.filter(date_stamp=date_stamp)
            assert len(aa) < 2

            his = aa[0] if aa else MyStockHistorical(stock=stock,
                                                     date_stamp=date_stamp)
            his.open_price = Decimal(details['1. open'])
            his.high_price = Decimal(details['2. high'])
            his.low_price = Decimal(details['3. low'])
            his.close_price = Decimal(details['4. close'])
            his.vol = int(details['5. volume'])
            to_save[date_stamp] = his

        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=full&apikey=4W4899YHR2QYOFQ2' % symbol
        adjusted = self.http_handler.request(url)
        adjusted = json.loads(adjusted)
        logger.debug('[%s]:  reading adjusted daily historicals' % symbol)
        for day, details in adjusted['Time Series (Daily)'].items():
            ds = day.split('-')
            date_stamp = dt(year=int(ds[0]), month=int(ds[1]), day=int(ds[2]))
            his = to_save[date_stamp]

            his.adj_open = Decimal(details['1. open'])
            his.adj_high = Decimal(details['2. high'])
            his.adj_low = Decimal(details['3. low'])
            his.close_price = Decimal(details['4. close'])
            his.adj_close = Decimal(details['5. adjusted close'])
            his.vol = int(details['6. volume'])
            his.adj_factor = float(details['8. split coefficient'])

        # ok so we now save

        logger.debug('[%s]:  writing historicals to DB. This can take a while.' % symbol)
        for obj in to_save.values():
            obj.save()


@shared_task
def stock_historical_alpha_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockHistoricalAlphaVantage(http_agent)
    crawler.parser(symbol)
