# -*- coding: utf-8 -*-
from __future__ import absolute_import

import csv
import datetime as dt
import inspect
import itertools
import logging
import sys
import time
from datetime import timedelta
from decimal import Decimal
from decimal import InvalidOperation
from functools import reduce
from itertools import izip_longest
from math import cos
from math import sin

import cPickle
import numpy as np
import simplejson as json
import StringIO
from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from numpy import mean
from numpy import std
from scipy import stats

from stock.models import MySimulationCondition
from stock.models import MySimulationSnapshot
from stock.models import MyStock
from stock.models import MyStockHistorical
from stock.utility import PlainUtility

logger = logging.getLogger("jk")


def grouper(iterable, n, padvalue=None):
    # grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'),
    # ('g','x','x')
    return list(izip_longest(*[iter(iterable)] * n, fillvalue=padvalue))


class MyStockFlagSP500:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self):
        # clear is_sp500 flag
        for s in MyStock.objects.all():
            s.is_sp500 = False
            s.save()

        url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv"
        content = self.http_handler.request(url)
        # logger.debug(content)

        f = StringIO.StringIO(content)
        for index, vals in enumerate(csv.reader(f)):
            if not index:
                continue
            if len(vals) != 3:
                logger.error("[%s] error, %d" % (vals[0], len(vals)))
                continue

            stock, created = MyStock.objects.get_or_create(symbol=vals[0])
            stock.company_name = vals[1]
            stock.is_sp500 = True
            stock.sector = vals[-1]
            stock.save()
            logger.debug("[%s] complete" % vals[0])


@shared_task
def stock_flag_sp500_consumer():
    http_agent = PlainUtility()
    crawler = MyStockFlagSP500(http_agent)
    crawler.parser()


class MyStockPrevYahoo:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now - timedelta(7)

        date_str = "a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d" % (
            now.month - 1,
            now.day,
            now.year,
            ago.month - 1,
            ago.day,
            ago.year,
        )
        url = "http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv" % (
            symbol,
            date_str,
        )
        logger.debug(url)
        content = self.http_handler.request(url)

        stock = MyStock.objects.get(symbol=symbol)
        f = StringIO.StringIO(content)
        for vals in csv.reader(f):
            if len(vals) != 7:
                logger.error("[%s] error, %d" % (symbol, len(vals)))
            elif "Open" in vals[1]:
                continue  # title line
            else:
                stock.prev_open = Decimal(vals[1])
                stock.prev_high = Decimal(vals[2])
                stock.prev_low = Decimal(vals[3])
                stock.prev_close = Decimal(vals[4])
                stock.prev_change = (
                    (stock.prev_open - stock.prev_close)
                    / stock.prev_open
                    * Decimal(100.0)
                )
                stock.save()
                logger.debug("[%s] complete" % symbol)
                break


@shared_task
def stock_prev_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevYahoo(http_agent)
    crawler.parser(symbol)


class MyStockPrevWeekYahoo:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now - timedelta(weeks=1)

        date_str = "a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d" % (
            ago.month - 1,
            ago.day,
            ago.year,
            now.month - 1,
            now.day,
            now.year,
        )
        url = "http://ichart.yahoo.com/table.csv?s=%s&%s&g=d&ignore=.csv" % (
            symbol,
            date_str,
        )
        logger.debug(url)
        content = self.http_handler.request(url)

        stock = MyStock.objects.get(symbol=symbol)
        adj_close = []
        f = StringIO.StringIO(content)
        cnt = 0
        for vals in csv.reader(f):
            if len(vals) != 7:
                logger.error("[%s] error, %d" % (symbol, len(vals)))
            elif "Adj" in vals[-1]:
                continue
            elif cnt < 7:
                adj_close.append(vals[-1])
                cnt += 1
            elif cnt >= 7:
                break

        # persist
        stock.week_adjusted_close = ",".join(list(reversed(adj_close)))
        stock.save()
        logger.debug("[%s] complete" % symbol)


@shared_task
def stock_prev_week_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevWeekYahoo(http_agent)
    crawler.parser(symbol)


class MyStockPrevMonthYahoo:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now + relativedelta(months=-1)

        date_str = "a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d" % (
            ago.month - 1,
            ago.day,
            ago.year,
            now.month - 1,
            now.day,
            now.year,
        )
        url = "http://ichart.yahoo.com/table.csv?s=%s&%s&g=w&ignore=.csv" % (
            symbol,
            date_str,
        )
        logger.debug(url)
        content = self.http_handler.request(url)

        stock = MyStock.objects.get(symbol=symbol)
        adj_close = []
        f = StringIO.StringIO(content)
        cnt = 0
        for vals in csv.reader(f):
            if len(vals) != 7:
                logger.error("[%s] error, %d" % (symbol, len(vals)))
            elif "Adj" in vals[-1]:
                continue
            elif cnt < 4:
                adj_close.append(vals[-1])
                cnt += 1
            elif cnt >= 4:
                break

        # persist
        stock.month_adjusted_close = ",".join(list(reversed(adj_close)))
        stock.save()
        logger.debug("[%s] complete" % symbol)


@shared_task
def stock_prev_month_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevMonthYahoo(http_agent)
    crawler.parser(symbol)


class MyStockPrevFibYahoo:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbol):
        stock = MyStock.objects.get(symbol=symbol)
        fib = [5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        fib_ratio = [
            a / 100 for a in [0.0, 23.6, 38.2, 50, 61.8, 100, 161.8, 261.8, 423.6]
        ]

        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        now = dt.now()
        ago = now + relativedelta(months=-180)

        date_str = "a=%d&b=%d&c=%d%%20&d=%d&e=%d&f=%d" % (
            ago.month - 1,
            ago.day,
            ago.year,
            now.month - 1,
            now.day,
            now.year,
        )
        for interval in ["w", "d"]:
            url = "http://ichart.yahoo.com/table.csv?s=%s&%s&g=%s&ignore=.csv" % (
                symbol,
                date_str,
                interval,
            )
            logger.debug(url)
            content = self.http_handler.request(url)
            adj_close = []

            f = StringIO.StringIO(content)
            for cnt, vals in enumerate(csv.reader(f)):
                if len(vals) != 7:
                    logger.error("[%s] error, %d" % (symbol, len(vals)))
                elif "Adj" in vals[-1]:
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
            if interval == "w":
                stock.fib_weekly_adjusted_close = ",".join(adj_close)

                stock.fib_weekly_score = sum([a * b for a, b in zip(tmp, fib_ratio)])
            elif interval == "d":
                stock.fib_daily_adjusted_close = ",".join(adj_close)
                stock.fib_daily_score = sum([a * b for a, b in zip(tmp, fib_ratio)])

            stock.save()
        logger.debug("[%s] complete" % symbol)


@shared_task
def stock_prev_fib_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockPrevFibYahoo(http_agent)
    crawler.parser(symbol)


class MyStockHistoricalYahoo:
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
        stock, created = MyStock.objects.get_or_create(symbol=symbol)
        his = [
            x.isoformat()
            for x in MyStockHistorical.objects.filter(stock=stock).values_list(
                "date_stamp", flat=True
            )
        ]

        # Read Yahoo api to get data
        # https://code.google.com/p/yahoo-finance-managed/wiki/csvHistQuotesDownload
        unix_origin = dt(1970, 1, 1)
        now = dt.now()
        ago = now + relativedelta(years=-50)  # 50 years

        # https://query1.finance.yahoo.com/v7/finance/download/AMZN?period1=863654400&period2=1607990400&interval=1d&events=history&includeAdjustedClose=true

        date_str = "period1={}&period2={}".format(
            int((ago - unix_origin).total_seconds()),
            int((now - unix_origin).total_seconds()),
        )
        url = "https://query1.finance.yahoo.com/v7/finance/download/{}?{}&interval=1d&events=history&includeAdjustedClose=true".format(
            symbol, date_str
        )
        logger.debug(url)
        content = self.http_handler.request(url)

        # Parse data to update stock historicals
        f = StringIO.StringIO(content)
        records = []
        for cnt, vals in enumerate(csv.reader(f)):
            if not self._are_vals_valid(symbol, vals):
                continue

            # stamp = [int(v) for v in vals[0].split('-')]
            # date_stamp = dt(year=stamp[0], month=stamp[1], day=stamp[2])
            date_stamp = dt.strptime(vals[0], "%Y-%m-%d")
            if date_stamp.date().isoformat() in his:
                # logger.debug('already have this')
                continue  # we already have these
            else:
                open_p, high_p, low_p, close_p, adj_p = map(
                    self._convert_to_decimal, vals[1:6]
                )

                try:
                    vol = int(vals[6]) / 1000.0
                except InvalidOperation:
                    vol = -1

                # Create an obj and wait for bulk creation
                h = MyStockHistorical(
                    stock=stock,
                    date_stamp=date_stamp,
                    open_price=open_p,
                    high_price=high_p,
                    low_price=low_p,
                    close_price=close_p,
                    vol=vol,
                    adj_close=adj_p,
                )
                records.append(h)

                # bulk creation
                if len(records) >= 1000:
                    MyStockHistorical.objects.bulk_create(records)
                    records = []

        # whatever left in records are to be saved to DB
        if records:
            MyStockHistorical.objects.bulk_create(records)

        # persist
        logger.debug("[%s] complete" % symbol)

    def _convert_to_decimal(self, val):
        try:
            me = Decimal(val)
        except InvalidOperation:
            me = Decimal(-1)
        return me

    def _are_vals_valid(self, symbol, vals):
        if not vals:
            # protect from blank line or invalid symbol, eg. China
            # stock symbols logger.debug('not vals')
            return False

        if not reduce(lambda x, y: x and y, vals):
            # any empty string, None will be skipped
            # logger.debug('not all columns have value')
            return False

        if len(vals) != 7:
            logger.error("[%s] error, %d" % (symbol, len(vals)))
            return False

        elif "Adj" in vals[-2]:
            # this is to skip the column header line
            return False


@shared_task
def stock_historical_yahoo_consumer(symbol):
    http_agent = PlainUtility()
    crawler = MyStockHistoricalYahoo(http_agent)
    crawler.parser(symbol)


class MyStockMonitorYahoo:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbols):
        # https://greenido.wordpress.com/2009/12/22/yahoo-finance-hidden-api/
        url = "http://finance.yahoo.com/d/quotes.csv?s=%s&f=srpoabvf6ml1n" % symbols
        content = self.http_handler.request(url)
        # logger.debug(content)

        f = StringIO.StringIO(content)
        for vals in csv.reader(f):
            if len(vals) != 11:
                logger.error("[%s] error, %d" % (vals[0], len(vals)))
                continue

            stock = MyStock.objects.get(symbol=vals[0])
            try:
                stock.pe = Decimal(vals[1])
            except InvalidOperation:
                pass

            # at least we want the daily open
            if vals[3] == "N/A":
                continue
            stock.day_open = Decimal(vals[3])

            try:
                stock.ask = Decimal(vals[4])
            except InvalidOperation:
                pass
            try:
                stock.bid = Decimal(vals[5])
            except InvalidOperation:
                pass

            stock.vol = int(vals[6]) / 1000.0

            try:
                stock.float_share = float(vals[7]) / 1000000
            except ValueError:
                pass  # could be N/A

            if "-" in vals[8]:
                stock.day_low = Decimal(vals[8].split("-")[0])
                stock.day_high = Decimal(vals[8].split("-")[1])

            stock.last = Decimal(vals[9])
            stock.company_name = vals[10]
            stock.save()
            logger.debug("[%s] complete" % vals[0])


@shared_task
def stock_monitor_yahoo_consumer(symbols):
    http_agent = PlainUtility()
    crawler = MyStockMonitorYahoo(http_agent)
    crawler.parser(symbols)


class MyStockMonitorYahoo2:
    def __init__(self, handler):
        self.http_handler = handler
        self.agent = handler.agent

    def parser(self, symbols):
        # We are passing in symboles in CSV format,
        # if nothing is here, skip.
        if not len(symbols):
            return

        url = (
            "http://finance.yahoo.com/webservice/v1/symbols/%s/quote?format=json&view=detail"
            % symbols
        )
        content = self.http_handler.request(url)
        content = json.loads(content)
        for r in content["list"]["resources"]:
            fields = r["resource"]["fields"]
            symbol = fields["symbol"]

            try:
                stock = MyStock.objects.get(symbol=symbol)
            except ObjectDoesNotExist:
                logger.error(
                    "MyStockMonitorYahoo2: symbol [%s] not found in DB" % symbol
                )
                continue

            stock.last = Decimal(fields["price"])

            # last update time
            stock.save()
            logger.debug("[%s] complete" % symbol)


@shared_task
def stock_monitor_yahoo_consumer2(symbols):
    http_agent = PlainUtility()
    crawler = MyStockMonitorYahoo2(http_agent)
    crawler.parser(symbols)


class MyStockBacktesting_1:
    def __init__(self):
        pass

    def parser(self, symbol):
        logger.debug("%s starting" % symbol)
        exec_start = time.time()

        records = MyStockHistorical.objects.filter(stock__symbol=symbol).order_by(
            "date_stamp"
        )

        # The starting point is depending on how much past data your strategy is calling for.
        # For example, if we are to calculate 10 weeks of fib score, we need at
        # least 10 weeks of history data.
        start = 10
        if start > len(records):
            logger.error("%s: not enough data" % symbol)
            return

        t0 = None
        for i in range(start, len(records)):
            logger.debug("%s: %d/%d" % (symbol, i, len(records)))
            prev_d = records[i - 1]
            t0 = records[i]  # set T0
            now = t0.date_stamp

            # day changes
            # simulate a middle point between high and low as spot
            spot = float(t0.high_price + t0.low_price) / 2.0
            oneday_change = (spot - float(t0.open_price)) / float(t0.open_price) * 100.0
            twoday_change = (
                (spot - float(prev_d.open_price)) / float(prev_d.open_price) * 100.0
            )

            # week changes
            ago = now + relativedelta(days=-5)  # search for last week's
            prev_week = records.filter(stock=t0.stock, date_stamp=ago)
            if prev_week:
                prev_week = prev_week[0]
            else:
                continue  # not enough data points for this strategy
            week_change = (
                (spot - float(prev_week.open_price))
                / float(prev_week.open_price)
                * 100.0
            )

            # month changes
            ago = now + relativedelta(months=-1)  # search for last month's
            prev_mon = records.filter(stock=t0.stock, date_stamp=ago)
            if prev_mon:
                prev_mon = prev_mon[0]
            else:
                continue  # not enough data points for this strategy
            month_change = (
                (spot - float(prev_mon.open_price)) / float(prev_mon.open_price) * 100.0
            )

            # consistency
            if (
                oneday_change > 0
                and twoday_change > 0
                and week_change > 0
                and month_change > 0
            ):
                trend_is_consistent_gain = True
            else:
                trend_is_consistent_gain = False

            if (
                oneday_change < 0
                and twoday_change < 0
                and week_change < 0
                and month_change < 0
            ):
                trend_is_consistent_loss = True
            else:
                trend_is_consistent_loss = False

            """
            Strategy: marked as "G" if trend is consistently gaining, "L" if consistently losing, "U" if otherwise.
            """
            if trend_is_consistent_gain:
                t0.flag_by_strategy = "G"  # "gain"
            elif trend_is_consistent_loss:
                t0.flag_by_strategy = "L"  # "loss"
            else:
                t0.flag_by_strategy = "U"  # stands for "unknown"

            # save to DB
            t0.save()

        logger.debug("%s completed, elapse %f" % (symbol, time.time() - exec_start))


@shared_task
def backtesting_s1_consumer(symbol):
    crawler = MyStockBacktesting_1()
    crawler.parser(symbol)


class MyStockBacktestingSimulation:
    def __init__(self, condition):
        # Model MySimulation is not json-able, so we are passing it
        # over as python pickle, so cool!
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
            simulation=self.condition
        )
        if is_update:
            existing_results.delete()
        elif len(existing_results):
            return

        logger.debug("%s simulation starting" % self.condition)

        # simulate tradings
        exec_start = time.time()
        simulation_methods = {
            1: "MySimulationAlpha",
            2: "MySimulationBuyLowSellHigh",
            3: "MySimulationBuyHighSellLow",
        }
        trading_method = getattr(
            sys.modules[__name__], simulation_methods[self.condition.strategy]
        )
        simulator = trading_method(user, simulation=self.condition)
        simulator.run()

        logger.debug(
            " %s simulation end %f" % (self.condition, time.time() - exec_start)
        )


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
        logger.debug("%s starting" % symbol)
        exec_start = time.time()

        records = MyStockHistorical.objects.filter(stock__symbol=symbol).order_by(
            "date_stamp"
        )

        # The starting point is depending on how much past data your
        # strategy is calling for.  For example, if we are to
        # calculate 10 weeks of fib score, we need at least 10 weeks
        # of history data.
        if window_length > len(records):
            logger.error("%s: not enough data" % symbol)
            return

        for i in range(window_length, len(records)):
            logger.debug("%s: %d/%d" % (symbol, i, len(records)))

            # sliding window
            window = records[i - window_length : i]

            # set T0
            t0 = records[i]

            # compute value
            self.compute_value(t0, window)

            # save to DB
            t0.save()

        logger.debug("%s completed, elapse %f" % (symbol, time.time() - exec_start))

    def compute_value(self, t0, window):
        """Overriden by child class to execute computation."""
        pass


class MyStockDailyReturn(MyStockStrategyValue):
    """Daily return % using adj close.

    Compute historical oneday_change = (today's close - prev's
    close)/prev's close *100

    """

    def __init__(self):
        super(MyStockDailyReturn, self).__init__()

    def compute_value(self, t0, window):
        prev = window[-1]

        # compute daily return
        if t0.adj_close > 0 and t0.open_price > 0:
            t0.daily_return = (t0.adj_close - t0.open_price) / t0.open_price * 100
        elif t0.close_price > 0 and t0.open_price > 0:
            t0.daily_return = (t0.close_price - t0.open_price) / t0.open_price * 100

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

        t0.relative_hl = -100 * (ref_high - t0.close_price) / (ref_high - ref_low) + 50


@shared_task
def backtesting_relative_hl_consumer(symbol):
    crawler = MyStockRelativeHL()
    crawler.run(symbol, 40)


class MyStockRelativeMovingAvg(MyStockStrategyValue):
    """Relative Position Indicator.

    Using moving Average= (Price - Average(Price,Len))/StdDev(Price,Len).
    Len is 40 by default.
    """

    def __init__(
        self,
    ):
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

    def __init__(
        self,
    ):
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

    def __init__(
        self,
    ):
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

    def __init__(
        self,
    ):
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

    def __init__(
        self,
    ):
        super(MyStockDecyclerOscillator, self).__init__()

    def compute_value(self, t0, window):
        period = 10
        k = 1
        price = t0.close_price
        alpha1 = (cos(0.707 * 360 / period) + sin(0.707 * 360 / period) - 1) / cos(
            0.707 * 360 / period
        )
        logger.debug(period, k, price, alpha1)


@shared_task
def backtesting_decycler_oscillator_consumer(symbol):
    crawler = MyStockDecyclerOscillator()
    crawler.run(symbol, 3)


@shared_task
def batch_simulation_daily_return(
    date_range, strategies=[1, 2], capital=10000, per_trade=1000
):
    sources = [1]
    strategy_values = [1]

    # simulation run
    for (source, strategy, strategy_value) in itertools.product(
        sources, strategies, strategy_values
    ):
        start, end = date_range
        # we only try strategy 2 with source 1
        if strategy == 2 and source != 1:
            continue

        # simulation parameters
        logger.info(source, strategy, strategy_value, start, end)

        # cutoffs have different meanings based on strategy
        if strategy == 1:
            step = 25
            buy_cutoff = range(0, 100, step)
            sell_cutoff = [b + step for b in buy_cutoff]
            cutoffs = zip(buy_cutoff, sell_cutoff)
        elif strategy == 2:
            buy_cutoff = range(1, 6, 1)
            sell_cutoff = range(1, 6, 1)
            cutoffs = itertools.product(buy_cutoff, sell_cutoff)
            # cutoffs = [(1,1)]
        elif strategy == 3:
            buy_cutoff = range(1, 6, 1)
            sell_cutoff = range(1, 6, 1)
            cutoffs = itertools.product(buy_cutoff, sell_cutoff)

        # Set up simulation condition objects based on combination
        # of specified parameters. Note that the count of this
        # matrix increases dramatically if we expand this
        # parameter list.
        for (buy_cutoff, sell_cutoff) in cutoffs:
            condition, created = MySimulationCondition.objects.get_or_create(
                data_source=source,
                data_sort=1,  # descending
                strategy=strategy,
                strategy_value=strategy_value,
                start=start,
                end=end,
                capital=capital,
                per_trade=per_trade,
                buy_cutoff=buy_cutoff,
                sell_cutoff=sell_cutoff,
            )

            # if condition.data_source == 1 and strategy == 2:
            # MySimulationCondition is not json-able, using python pickle
            # instead. The downside of this is that we are relying on a
            # python-specif data format.  But it is safe in this context.
            if strategy in [2, 3]:
                # buy low sell high
                # Set is_update=True will remove all
                # existing results first and then rerun all
                # simulations. This is necessary because SP500 is gettting
                # new data each day.
                is_update = True
            else:
                # alpha
                # Because computing alpha index values are very time consuming,
                # so we are to skip existing results to save time. Ideally
                # we should set is_update=True to recompute from a clean sheet.
                is_update = False

            crawler = MyStockBacktestingSimulation(cPickle.dumps(condition))
            crawler.run(is_update)


class MyBatchHandler:
    def __init__(self):
        pass

    @classmethod
    def batch_simulation_daily_return(
        self, date_range, strategies=[1, 2], capital=10000, per_trade=1000
    ):
        sources = [
            1,
        ]
        strategy_values = [1]

        # simulation run
        for (source, strategy, strategy_value) in itertools.product(
            sources, strategies, strategy_values
        ):
            for (start, end) in date_range:
                # we only try strategy 2 with source 1
                if strategy == 2 and source != 1:
                    continue

                # simulation parameters
                logger.info(source, strategy, strategy_value, start, end)

                # cutoffs have different meanings based on strategy
                if strategy == 1:
                    step = 25
                    buy_cutoff = range(0, 100, step)
                    sell_cutoff = [b + step for b in buy_cutoff]
                    cutoffs = zip(buy_cutoff, sell_cutoff)
                elif strategy == 2:
                    buy_cutoff = range(1, 6, 1)
                    sell_cutoff = range(1, 6, 1)
                    cutoffs = itertools.product(buy_cutoff, sell_cutoff)
                    # cutoffs = [(1,1)]
                elif strategy == 3:
                    buy_cutoff = range(1, 6, 1)
                    sell_cutoff = range(1, 6, 1)
                    cutoffs = itertools.product(buy_cutoff, sell_cutoff)

                # Set up simulation condition objects based on combination
                # of specified parameters. Note that the count of this
                # matrix increases dramatically if we expand this
                # parameter list.
                for (buy_cutoff, sell_cutoff) in cutoffs:
                    condition, created = MySimulationCondition.objects.get_or_create(
                        data_source=source,
                        data_sort=1,  # descending
                        strategy=strategy,
                        strategy_value=strategy_value,
                        start=start,
                        end=end,
                        capital=capital,
                        per_trade=per_trade,
                        buy_cutoff=buy_cutoff,
                        sell_cutoff=sell_cutoff,
                    )

                    # if condition.data_source == 1 and strategy == 2:
                    # MySimulationCondition is not json-able, using python pickle
                    # instead. The downside of this is that we are relying on a
                    # python-specif data format.  But it is safe in this context.
                    if strategy in [2, 3]:
                        # buy low sell high
                        # Set is_update=True will remove all
                        # existing results first and then rerun all
                        # simulations. This is necessary because SP500 is gettting
                        # new data each day.
                        backtesting_simulation_consumer.delay(
                            cPickle.dumps(condition), is_update=True
                        )
                    else:
                        # alpha
                        # Because computing alpha index values are very time consuming,
                        # so we are to skip existing results to save time. Ideally
                        # we should set is_update=True to recompute from a clean sheet.
                        backtesting_simulation_consumer.delay(
                            cPickle.dumps(condition), is_update=False
                        )

    @classmethod
    def rerun_existing_simulations(self, strategy=2):
        total_count = MySimulationCondition.objects.all().count()
        for counter, condition in enumerate(
            MySimulationCondition.objects.filter(strategy=strategy)
        ):
            logger.debug("%s: %d/%d" % (inspect.stack()[1][3], counter, total_count))

            # simulation run
            backtesting_simulation_consumer.delay(
                cPickle.dumps(condition), is_update=True
            )
