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

#################################
#
#   Alpha strategy values
#
#################################
from numpy import mean
from numpy import std
from scipy import stats
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


class MyStockPrevYahoo():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now - timedelta(7)

        date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d' % (
            now.month - 1, now.day, now.year, ago.month - 1, ago.day, ago.year)
        url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (
            symbol, date_str)
        logger.debug(url)
        content = self.http_handler.request(url)

        stock = MyStock.objects.get(symbol=symbol)
        f = StringIO.StringIO(content)
        for vals in csv.reader(f):
            if len(vals) != 7:
                logger.error('[%s] error, %d' % (symbol, len(vals)))
            elif 'Open' in vals[1]:
                continue  # title line
            else:
                stock.prev_open = Decimal(vals[1])
                stock.prev_high = Decimal(vals[2])
                stock.prev_low = Decimal(vals[3])
                stock.prev_close = Decimal(vals[4])
                stock.prev_change = (
                    stock.prev_open - stock.prev_close) / stock.prev_open * Decimal(100.0)
                stock.save()
                logger.debug('[%s] complete' % symbol)
                break


@shared_task
def stock_prev_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevYahoo(http_agent)
    crawler.parser(symbol)


class MyStockPrevWeekYahoo():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now - timedelta(weeks=1)

        date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d' % (
            ago.month - 1, ago.day, ago.year, now.month - 1, now.day, now.year)
        url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (
            symbol, date_str)
        logger.debug(url)
        content = self.http_handler.request(url)

        stock = MyStock.objects.get(symbol=symbol)
        adj_close = []
        f = StringIO.StringIO(content)
        cnt = 0
        for vals in csv.reader(f):
            if len(vals) != 7:
                logger.error('[%s] error, %d' % (symbol, len(vals)))
            elif 'Adj' in vals[-1]:
                continue
            elif cnt < 7:
                adj_close.append(vals[-1])
                cnt += 1
            elif cnt >= 7:
                break

        # persist
        stock.week_adjusted_close = ','.join(list(reversed(adj_close)))
        stock.save()
        logger.debug('[%s] complete' % symbol)


@shared_task
def stock_prev_week_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevWeekYahoo(http_agent)
    crawler.parser(symbol)


class MyStockPrevMonthYahoo():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now + relativedelta(months=-1)

        date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d' % (
            ago.month - 1, ago.day, ago.year, now.month - 1, now.day, now.year)
        url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=w&ignore=.csv' % (
            symbol, date_str)
        logger.debug(url)
        content = self.http_handler.request(url)

        stock = MyStock.objects.get(symbol=symbol)
        adj_close = []
        f = StringIO.StringIO(content)
        cnt = 0
        for vals in csv.reader(f):
            if len(vals) != 7:
                logger.error('[%s] error, %d' % (symbol, len(vals)))
            elif 'Adj' in vals[-1]:
                continue
            elif cnt < 4:
                adj_close.append(vals[-1])
                cnt += 1
            elif cnt >= 4:
                break

        # persist
        stock.month_adjusted_close = ','.join(list(reversed(adj_close)))
        stock.save()
        logger.debug('[%s] complete' % symbol)


@shared_task
def stock_prev_month_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevMonthYahoo(http_agent)
    crawler.parser(symbol)


class MyStockPrevFibYahoo():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        stock = MyStock.objects.get(symbol=symbol)
        fib = [5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        fib_ratio = [a / 100 for a in [0.0, 23.6,
                                       38.2, 50, 61.8, 100, 161.8, 261.8, 423.6]]

        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now + relativedelta(months=-180)

        date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d' % (
            ago.month - 1, ago.day, ago.year, now.month - 1, now.day, now.year)
        for interval in ['w', 'd']:
            url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=%s&ignore=.csv' % (
                symbol, date_str, interval)
            logger.debug(url)
            content = self.http_handler.request(url)
            adj_close = []

            f = StringIO.StringIO(content)
            for cnt, vals in enumerate(csv.reader(f)):
                if len(vals) != 7:
                    logger.error('[%s] error, %d' % (symbol, len(vals)))
                elif 'Adj' in vals[-1]:
                    continue
                elif cnt in fib:
                    adj_close.append(vals[-1])
                elif cnt > fib[-1]:
                    break  # no more need

            # compute diff = T(n+1)-T(n)
            adj_close = list(reversed(adj_close))
            tmp = [float(a) for a in adj_close]
            tmp = [a - b for a, b in zip(tmp[1:], tmp)]
            # persist
            if interval == 'w':
                stock.fib_weekly_adjusted_close = ','.join(adj_close)

                stock.fib_weekly_score = sum(
                    [a * b for a, b in zip(tmp, fib_ratio)])
            elif interval == 'd':
                stock.fib_daily_adjusted_close = ','.join(adj_close)
                stock.fib_daily_score = sum(
                    [a * b for a, b in zip(tmp, fib_ratio)])

            stock.save()
        logger.debug('[%s] complete' % symbol)


@shared_task
def stock_prev_fib_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevFibYahoo(http_agent)
    crawler.parser(symbol)


class MyStockHistoricalYahoo():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        """Parse Yahoo api stock historical data.

        Polling ichart.yahoo.com with manufactured query string (dark magic)
        to get historical data of a given stock symbol.

        Arguments:
            :symbol: stock symbol

        Return:
            none
        """

        # Get stock and its existing historicals
        stock = MyStock.objects.get(symbol=symbol)
        his = [x.isoformat() for x in MyStockHistorical.objects.filter(
            stock=stock).values_list('date_stamp', flat=True)]

        # Read Yahoo api to get data
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now + relativedelta(years=-20)  # 20 years

        date_str = 'a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d' % (
            ago.month, ago.day, ago.year, now.month, now.day, now.year + 1)
        url = 'http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv' % (
            symbol, date_str)
        logger.debug(url)
        content = self.http_handler.request(url)

        # Parse data to update stock historicals
        f = StringIO.StringIO(content)
        records = []
        for cnt, vals in enumerate(csv.reader(f)):
            # logger.debug(vals)
            if not vals:
                # protect from blank line or invalid symbol, eg. China stock symbols
                # logger.debug('not vals')
                continue
            elif not reduce(lambda x, y: x and y, vals):
                # any empty string, None will be skipped
                # logger.debug('not all columns have value')
                continue
            elif len(vals) != 7:
                logger.error('[%s] error, %d' % (symbol, len(vals)))
                continue
            elif 'Adj' in vals[-1]:
                # this is to skip the column header line
                continue

            # stamp = [int(v) for v in vals[0].split('-')]
            # date_stamp = dt(year=stamp[0], month=stamp[1], day=stamp[2])
            date_stamp = dt.strptime(vals[0], '%Y-%m-%d')
            if date_stamp.date().isoformat() in his:
                # logger.debug('already have this')
                continue  # we already have these
            else:
                try:
                    open_p = Decimal(vals[1])
                except:
                    open_p = Decimal(-1)
                try:
                    high_p = Decimal(vals[2])
                except:
                    high_p = Decimal(-1)
                try:
                    low_p = Decimal(vals[3])
                except:
                    low_p = Decimal(-1)
                try:
                    close_p = Decimal(vals[4])
                except:
                    close_p = Decimal(-1)
                try:
                    vol = int(vals[5]) / 1000.0
                except:
                    vol = -1
                try:
                    adj_p = Decimal(vals[6])
                except:
                    adj_p = Decimal(-1)
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

        # whatever left in records are to be saved to DB
        if records:
            MyStockHistorical.objects.bulk_create(records)

        # persist
        logger.debug('[%s] complete' % symbol)


@shared_task
def stock_historical_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockHistoricalYahoo(http_agent)
    crawler.parser(symbol)


class MyStockMonitorYahoo():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbols):
        # https://greenido.wordpress.com/2009/12/22/yahoo-finance-hidden-api/
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=srpoabvf6ml1n' % symbols
        content = self.http_handler.request(url)
        # logger.debug(content)

        f = StringIO.StringIO(content)
        for vals in csv.reader(f):
            if len(vals) != 11:
                logger.error('[%s] error, %d' % (vals[0], len(vals)))
                continue

            stock = MyStock.objects.get(symbol=vals[0])
            try:
                stock.pe = Decimal(vals[1])
            except:
                pass

            # at least we want the daily open
            if vals[3] == 'N/A':
                continue
            stock.day_open = Decimal(vals[3])

            try:
                stock.ask = Decimal(vals[4])
            except:
                pass
            try:
                stock.bid = Decimal(vals[5])
            except:
                pass

            stock.vol = int(vals[6]) / 1000.0

            try:
                stock.float_share = float(vals[7]) / 1000000
            except:
                pass  # could be N/A

            if '-' in vals[8]:
                stock.day_low = Decimal(vals[8].split('-')[0])
                stock.day_high = Decimal(vals[8].split('-')[1])

            stock.last = Decimal(vals[9])
            stock.company_name = vals[10]
            stock.save()
            logger.debug('[%s] complete' % vals[0])


@shared_task
def stock_monitor_yahoo_consumer(symbols):
    http_agent = PlainUtility()
    crawler = MyStockMonitorYahoo(http_agent)
    crawler.parser(symbols)


class MyStockMonitorYahoo2():

    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbols):
        # We are passing in symboles in CSV format,
        # if nothing is here, skip.
        if not len(symbols):
            return

        url = 'http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json&view=detail' % symbols
        content = self.http_handler.request(url)
        content = json.loads(content)
        for r in content['list']['resources']:
            fields = r['resource']['fields']
            symbol = fields['symbol']

            try:
                stock = MyStock.objects.get(symbol=symbol)
            except:
                logger.error('MyStockMonitorYahoo2: symbol [%s] not found in DB' % symbol)
                continue

            stock.last = Decimal(fields['price'])

            # last update time
            stock.save()
            logger.debug('[%s] complete' % symbol)


@shared_task
def stock_monitor_yahoo_consumer2(symbols):
    http_agent = PlainUtility()
    crawler = MyStockMonitorYahoo2(http_agent)
    crawler.parser(symbols)


class MyImportChinaStock():

    def __init__(self):
        pass

    def parser(self, symbol, val_list):
        logger.info('processing %s' % symbol)
        stock = MyStock.objects.get(symbol=symbol)
        records = []
        cnt = 0
        total = len(val_list)
        for vals in val_list:
            if len(vals) < 10:
                logger.error('wrong length %s' % ','.join(vals))

            exec_start = time.time()
            date_stamp = dt(year=int(vals[1][:4]), month=int(
                vals[1][4:6]), day=int(vals[1][-2:]))
            open_p = Decimal(vals[2])
            high_p = Decimal(vals[3])
            low_p = Decimal(vals[4])
            close_p = Decimal(vals[5])
            vol = Decimal(vals[6])
            amount = Decimal(vals[7]) * Decimal(10.0)
            adj = Decimal(vals[8])
            status = int(vals[9])

            h = MyStockHistorical(
                stock=stock,
                date_stamp=date_stamp,
                open_price=open_p,
                high_price=high_p,
                low_price=low_p,
                close_price=close_p,
                vol=vol,
                amount=amount,
                status=status,

                # adjusted values
                adj_open=open_p * adj,
                adj_high=high_p * adj,
                adj_low=low_p * adj,
                adj_close=close_p * adj,
            )
            records.append(h)
            if len(records) >= 1000:
                MyStockHistorical.objects.bulk_create(records)
                cnt += len(records)
                records = []
                logger.info('%s inserted %d/%d' % (symbol, cnt, total))
        if len(records):
            MyStockHistorical.objects.bulk_create(records)
        logger.info('%s elapse %f' % (symbol, time.time() - exec_start))


@shared_task
def import_china_stock_consumer(symbol, val_list):
    crawler = MyImportChinaStock()
    crawler.parser(symbol, val_list)


class MyChenMin():

    def __init__(self):
        pass

    def parser(self, f, output=None):
        try:
            book = xlrd.open_workbook(f)
        except:
            logger.error('%s error' % f)
            return

        sh = book.sheet_by_index(0)
        if sh.name != u'账户对账单':
            logger.error(f)

        # range for 账户对账单
        first_col_vals = [sh.cell_value(rowx=i, colx=0)
                          for i in range(sh.nrows)]
        start = end = None
        for idx, val in enumerate(first_col_vals):
            if val == u'对帐单':
                start = idx
            if val == u'当日持仓清单':
                end = idx
            if start and end:
                break

        vals = []
        for row in xrange(start, end):
            vals.append([sh.cell_value(rowx=row, colx=c)
                         for c in range(sh.ncols)])

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
            executed_on = dt(year=yr, month=m, day=d)

            c = MyChenmin(
                executed_on=executed_on,
                transaction_type=transaction_type,
                symbol=symbol,
                name=name,
                price=price,
                vol=vol,
                total=total
            )
            c.save()
        logger.debug('%s done' % f)


@shared_task
def chenmin_consumer(files):
    crawler = MyChenMin()
    crawler.parser(files)


class MyStockInflux():

    def __init__(self):
        db_name = 'stock'
        self.client = InfluxDBClient(
            'localhost', 8086, 'root', 'root', db_name)
        # all_dbs_list = self.client.get_list_database()
        # that list comes back like: [{u'name': u'hello_world'}]
        # if db_name not in [str    (x['name']) for x in all_dbs_list]:
        #   print "Creating db {0}".format(db_name)
        #   self.client.create_database(db_name)
        # else:
        #   print "Reusing db {0}".format(db_name)
        self.client.switch_db(db_name)

    def parser(self, symbol):
        points = []
        for h in MyStockHistorical.objects.filter(stock__symbol=symbol).order_by('date_stamp'):
            points = [[h.id, h.date_stamp.strftime('%Y-%m-%d'), time.mktime(h.date_stamp.timetuple()), float(
                h.open_price), float(h.high_price), float(h.low_price), float(h.close_price), float(h.adj_close), h.vol]]

            self.client.write_points([{
                'name': symbol,
                'columns': ['id', 'date', 'time', 'open', 'high', 'low', 'close', 'adj_close', 'vol'],
                'points':points
            }], time_precision='s')

        logger.debug('%s completed' % symbol)


@shared_task
def influx_consumer(symbol):
    crawler = MyStockInflux()
    crawler.parser(symbol)


class MyStockBacktesting_1():

    def __init__(self):
        pass

    def parser(self, symbol):
        logger.debug('%s starting' % symbol)
        exec_start = time.time()

        records = MyStockHistorical.objects.filter(
            stock__symbol=symbol).order_by('date_stamp')

        # The starting point is depending on how much past data your strategy is calling for.
        # For example, if we are to calculate 10 weeks of fib score, we need at
        # least 10 weeks of history data.
        start = 10
        if start > len(records):
            logger.error('%s: not enough data' % symbol)
            return

        t0 = None
        for i in range(start, len(records)):
            logger.debug('%s: %d/%d' % (symbol, i, len(records)))
            prev_d = records[i - 1]
            t0 = records[i]  # set T0
            now = t0.date_stamp

            # day changes
            # simulate a middle point between high and low as spot
            spot = float(t0.high_price + t0.low_price) / 2.0
            oneday_change = (spot - float(t0.open_price)) / \
                float(t0.open_price) * 100.0
            twoday_change = (spot - float(prev_d.open_price)) / \
                float(prev_d.open_price) * 100.0

            # week changes
            ago = now + relativedelta(days=-5)  # search for last week's
            prev_week = records.filter(stock=t0.stock, date_stamp=ago)
            if prev_week:
                prev_week = prev_week[0]
            else:
                continue  # not enough data points for this strategy
            week_change = (spot - float(prev_week.open_price)) / \
                float(prev_week.open_price) * 100.0

            # month changes
            ago = now + relativedelta(months=-1)  # search for last month's
            prev_mon = records.filter(stock=t0.stock, date_stamp=ago)
            if prev_mon:
                prev_mon = prev_mon[0]
            else:
                continue  # not enough data points for this strategy
            month_change = (spot - float(prev_mon.open_price)) / \
                float(prev_mon.open_price) * 100.0

            # consistency
            if oneday_change > 0 and twoday_change > 0 and week_change > 0 and month_change > 0:
                trend_is_consistent_gain = True
            else:
                trend_is_consistent_gain = False

            if oneday_change < 0 and twoday_change < 0 and week_change < 0 and month_change < 0:
                trend_is_consistent_loss = True
            else:
                trend_is_consistent_loss = False

            """
            Strategy: marked as "G" if trend is consistently gaining, "L" if consistently losing, "U" if otherwise.
            """
            if trend_is_consistent_gain:
                t0.flag_by_strategy = 'G'  # "gain"
            elif trend_is_consistent_loss:
                t0.flag_by_strategy = 'L'  # "loss"
            else:
                t0.flag_by_strategy = 'U'  # stands for "unknown"

            # save to DB
            t0.save()

        logger.debug('%s completed, elapse %f' %
                     (symbol, time.time() - exec_start))


@shared_task
def backtesting_s1_consumer(symbol):
    crawler = MyStockBacktesting_1()
    crawler.parser(symbol)


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
            2: 'MySimulationBuyLowSellHigh',
            3: "MySimulationBuyHighSellLow"
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


class MyStockStrategyValue(object):
    """Abstract model that defines a "run" method
    that can overriden by children class to define
    their own compute_value method, which computes
    the so called index value per strategy.
    """

    def __init__(self):
        pass

    def run(self, symbol, window_length):
        logger.debug('%s starting' % symbol)
        exec_start = time.time()

        records = MyStockHistorical.objects.filter(
            stock__symbol=symbol).order_by('date_stamp')

        # The starting point is depending on how much past data your strategy is calling for.
        # For example, if we are to calculate 10 weeks of fib score, we need at
        # least 10 weeks of history data.
        if window_length > len(records):
            logger.error('%s: not enough data' % symbol)
            return

        for i in range(window_length, len(records)):
            logger.debug('%s: %d/%d' % (symbol, i, len(records)))

            # sliding window
            window = records[i - window_length:i]

            # set T0
            t0 = records[i]

            # compute value
            self.compute_value(t0, window)

            # save to DB
            t0.save()

        logger.debug('%s completed, elapse %f' %
                     (symbol, time.time() - exec_start))

    def compute_value(self, t0, window):
        """Overriden by child class to execute computation.
        """
        pass

class MyStockDailyReturn(MyStockStrategyValue):
    """Daily return value.

    Compute historical oneday_change = (today's close - prev's
    close)/prev's close *100

    """

    def __init__(self):
        super(MyStockDailyReturn, self).__init__()

    def compute_value(self, t0, window):
        prev = window[-1]

        # compute daily return
        if t0.adj_close > 0 and t0.open_price > 0:
            t0.daily_return = (t0.adj_close - t0.open_price) / \
                t0.open_price * 100
        elif t0.close_price > 0 and t0.open_price > 0:
            t0.daily_return = (
                t0.close_price - t0.open_price) / t0.open_price * 100

        # compute nightly return
        if t0.adj_close and prev.adj_close:
            t0.overnight_return = (t0.adj_close - prev.adj_close) / prev.adj_close * 100
        else:
            t0.overnight_return = 0


@shared_task
def backtesting_daily_return_consumer(symbol):
    crawler = MyStockDailyReturn()
    crawler.run(symbol, 2)


class MyStockRelativeHL(MyStockStrategyValue):
    """
    Relative Position indicator in (H,L) = -100*(Highest(High,Len)-Close)/(Highest(High,Len)-Lowest(Low,Len))+50;   // Len is 40 by default

    """

    def __init__(self):
        super(MyStockRelativeHL, self).__init__()

    def compute_value(self, t0, window):
        # compute index value
        ref_high = max([r.high_price for r in window])
        ref_low = min([r.low_price for r in window])

        t0.relative_hl = -100 * \
            (ref_high - t0.close_price) / (ref_high - ref_low) + 50


@shared_task
def backtesting_relative_hl_consumer(symbol):
    crawler = MyStockRelativeHL()
    crawler.run(symbol, 40)


class MyStockRelativeMovingAvg(MyStockStrategyValue):
    """Relative Position Indicator.

    Using moving Average= (Price - Average(Price,Len))/StdDev(Price,Len).
    Len is 40 by default.
    """

    def __init__(self,):
        super(MyStockRelativeMovingAvg, self).__init__()

    def compute_value(self, t0, window=40):
        ref_ma = mean([r.close_price for r in window])
        ref_std = std([r.close_price for r in window])

        # compute index value
        t0.val_by_strategy = (t0.close_price - ref_ma) / ref_std


@shared_task
def backtesting_relative_ma_consumer(symbol):
    crawler = MyStockRelativeMovingAvg()
    crawler.run(symbol, 40)


class MyStockCCI(MyStockStrategyValue):
    """CCI Indicator.

        MA = Average(Price,Len);
        value1=0;
        for i=0 to Len-1
                value1+ = |Price[i]-MA|;
        value1=value1/Len;
        CCI = (Price-MA)/(0.015*value1);
    """

    def __init__(self,):
        super(MyStockCCI, self).__init__()

    def compute_value(self, t0, window):
        ref_ma = mean([r.close_price for r in window])
        val = [r.close_price - ref_ma for r in window]
        cci = (t0.close_price - ref_ma) / (0.015 * val / len(window))

        # compute index value
        t0.val_by_strategy = cci


@shared_task
def backtesting_cci_consumer(symbol):
    crawler = MyStockCCI()
    crawler.run(symbol, 40)


class MyStockSI(MyStockStrategyValue):
    """SI indicator.
            K = max( |H - C[1]|, |L-C[1]|);
            R = the largest of :
                    if H-C[1],  then  |H-C[1]|-0.5|L-C[1]|+0.25|C[1]-O[1]|
                    if L-C[1],  then  |L-C[1]|-0.5|H-C[1]|+0.25|C[1]-O[1]|
                    if H-L,         then  H-L+0.25|C[1]-O[1]|
            SI Indicator = 50*(C-C[1] + 0.5*(C-O) + 0.25*(C[1]-O[1])*K/R
    """

    def __init__(self,):
        super(MyStockSI, self).__init__()

    def compute_value(self, t0, window):
        pass


@shared_task
def backtesting_si_consumer(symbol):
    crawler = MyStockSI()
    crawler.run(symbol, 40)


class MyStockLinearSlope(MyStockStrategyValue):
    """
    LinearRegSlope(Price, Len); // Len=3 by default
    """

    def __init__(self,):
        super(MyStockLinearSlope, self).__init__()

    def compute_value(self, t0, window):
        y = np.array([r.close_price for r in window].append(t0.close_price))
        x = np.array(range(1, len(y)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        t0.lg_slope = slope
        t0.save()


@shared_task
def backtesting_linear_slope_consumer(symbol):
    crawler = MyStockLinearSlope()
    crawler.run(symbol, 3)


class MyStockDecyclerOscillator(MyStockStrategyValue):
    """
    Decycler Oscillator (Price, HPPeriod, K);  HPPeriod=10, K=1
Alpha1= (Cos(0.707*360/HPPeriod) + Sin(0.707*360/HPPeriod)-1)/Cos(0.707*360/HPPeriod)
HP = (1-Alpha1/2) * (1-alpha1/2)*(Price-2*Price[1]+Price[2]) +
                2*(1-Alpha1)*HP[1] -(1-Alpha1)*(1-alpha1)*HP[2];
Decycle = Price-HP;
Alpha2 = (Cos(0.707*360/(0.5*HPPeriod)) + Sin(0.707*360/(0.5*HPPeriod))-1)/Cos(0.707*360/(0.5*HPPeriod))
DecycleOsc = (1-Alpha2/2) * (1-alpha2/2)*(Decycle-2*Decycle[1]+Decycle[2]) +
                2*(1-Alpha2)*DecycleOsc[1] -(1-Alpha2)*(1-alpha2)*DecycleOsc[2];
Indicator= 100*K*DecycleOsc/Price;
    """

    def __init__(self,):
        super(MyStockDecyclerOscillator, self).__init__()

    def compute_value(self, t0, window):
        period = 10
        k = 1
        price = t0.close_price
        alpha1 = (cos(0.707 * 360 / period) + sin(0.707 *
                                                  360 / period) - 1) / cos(0.707 * 360 / period)

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
