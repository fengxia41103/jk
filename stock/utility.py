#!/usr/bin/python
# -*- coding: utf-8 -*-

import cPickle
import datetime
import inspect
import itertools
import logging
import pprint
import random
import re
import shelve
import string
import sys
import time
import unittest
import urllib2
from datetime import date
from datetime import timedelta
from decimal import Decimal
from itertools import izip_longest
from unittest import TestCase
from unittest import TestSuite

import lxml.html
import simplejson as json
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
# available since 2.26.0
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import \
    WebDriverWait  # available since 2.4.0

# import models
from stock.models import MySimulationCondition
from stock.tasks import backtesting_simulation_consumer

logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):

    def default(self, obj):
        # handles both date and datetime objects
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return str(float(obj))
        else:
            return json.JSONEncoder.default(self, obj)


class ParametrizedTestCase(TestCase):
    """ TestCase classes that want to be parametrized should
        inherit from this class.
    """

    def __init__(self, methodName='runTest', param=None):
        super(ParametrizedTestCase, self).__init__(methodName)
        self.param = param

    @staticmethod
    def parametrize(testcase_klass, param=None):
        """ Create a suite containing all tests taken from the given
            subclass, passing them the parameter 'param'.
        """
        testloader = unittest.TestLoader()
        testnames = testloader.getTestCaseNames(testcase_klass)
        suite = unittest.TestSuite()
        for name in testnames:
            suite.addTest(testcase_klass(name, param=param))
        return suite


class MyDriver():

    def __init__(self):
        if BROWSER.lower() == 'ie':
            DesiredCapabilities.INTERNETEXPLORER[
                'ignoreProtectedModeSettings'] = True
            self.driver = webdriver.Ie()
        elif BROWSER.lower() == 'chrome':
            self.driver = webdriver.Chrome()
        elif BROWSER.lower() == 'firefox':
            self.driver = webdriver.Firefox()
        elif BROWSER.lower() == 'htmlunit':
            pass
            #server_url = "http://%s:%s/wd/hub" % (SELENIUM_RC_SERVER_IP, SELENIUM_RC_SERVER_PORT)
           #self.driver= webdriver.Remote(server_url,desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT.copy())


class MyPrettyPrinter(pprint.PrettyPrinter):

    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)


class MyUtility():

    def __init__(self):
        pass

    def illegal_characters(self, length=1):
        myrg = random.SystemRandom()
        return ''.join(myrg.choice(string.punctuation) for _ in range(length))

    def legal_characters(self, length=1):
        myrg = random.SystemRandom()
        return ''.join(myrg.choice(string.ascii_letters + string.digits) for _ in range(length))

    def integers(self, length=1, padding=None):
        myrg = random.SystemRandom()
        tmp = str(int(''.join(myrg.choice(string.digits)
                              for _ in range(length))))
        if padding:
            return tmp.zfill(int(padding))
        else:
            return tmp

    def floats(self, part_1, part_2):
        if part_2:
            return '%s.%s' % (self.integers(part_1), self.integers(part_2))
        else:
            return '%s' % self.integers(part_1)

    def period_around_today(self, gap=10):
        g = datetime.timedelta(days=gap)
        today = datetime.date(1971, 1, 1).today()
        start = today - g
        end = today + g
        return (start, end)

    def today_plus(self, plus=1):
        g = datetime.timedelta(days=plus)
        today = datetime.date(1971, 1, 1).today()
        return (today + g).strftime('%Y-%m-%d')

    def grouper(self, iterable, n, padvalue=None):
        # grouper('abcdefg', 3, 'x') --> ('a','b','c'), ('d','e','f'),
        # ('g','x','x')
        return list(izip_longest(*[iter(iterable)] * n, fillvalue=padvalue))

    @classmethod
    def sliding_windows(self, start_date, end_date, window_size):
        '''Create an array of [(starting date, ending date),] using a sliding
        window specified by `window_size`.

        For example, given starting ate of "2011-1-1" and window size
        10, you get first range of 2010/1/1-2010/1/10, then next is
        2010/1/2-2010/1/11, and so on. The last window in the series
        will be (end_date - 10 days, end_date).

        Args:
          start_date: starting date in ISO format &mdash; `year-month-day`
          end_date: ending date in ISO format
          window_size: number of days

        Returns:
          list: [(date ISO string,date ISO string),]

        '''

        delta = end_date - start_date

        sliding_windows = [(start_date + timedelta(days=i),
                            start_date + timedelta(days=i + window_size))
                           for i in range(delta.days - window_size)]
        return map(lambda (x, y): (x.isoformat(), y.isoformat()),
                   sliding_windows)


class MyBatchHandler():

    def __init__(self):
        pass

    @classmethod
    def batch_simulation_daily_return(self,
                                      date_range,
                                      strategies=[1, 2],
                                      capital=10000,
                                      per_trade=1000):
        sources = [1, ]
        strategy_values = [1]

        # simulation run
        for (source, strategy, strategy_value) in itertools.product(
                sources, strategies, strategy_values):
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
                        sell_cutoff=sell_cutoff
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
                            cPickle.dumps(condition), is_update=True)
                    else:
                        # alpha
                        # Because computing alpha index values are very time consuming,
                        # so we are to skip existing results to save time. Ideally
                        # we should set is_update=True to recompute from a clean sheet.
                        backtesting_simulation_consumer.delay(
                            cPickle.dumps(condition), is_update=False)

    @classmethod
    def rerun_existing_simulations(self, strategy=2):
        total_count = MySimulationCondition.objects.all().count()
        for counter, condition in enumerate(
                MySimulationCondition.objects.filter(strategy=strategy)):
            logger.debug('%s: %d/%d' % (inspect.stack()[1][3], counter, total_count))

            # simulation run
            backtesting_simulation_consumer.delay(
                cPickle.dumps(condition),
                is_update=True)
