#!/usr/bin/python
# -*- coding: utf-8 -*-

# setup Django
import codecs
import cPickle
import csv
import datetime as dt
import gc
import inspect
import itertools
# logging
import logging
import os
import os.path
import re
import sys
import time
import urllib
import urllib2
from datetime import date
from datetime import timedelta
from decimal import Decimal

import django
import lxml.html
import simplejson as json
import xlrd
from django.conf import settings
from django.db.models.loading import get_model
from django.utils import timezone
from influxdb.influxdb08 import InfluxDBClient

# import models
from stock.models import *
from stock.simulations import *
from stock.tasks import *
from stock.tasks import backtesting_daily_return_consumer
from stock.tasks import backtesting_relative_hl_consumer
from stock.tasks import backtesting_relative_ma_consumer
from stock.tasks import backtesting_s1_consumer
from stock.tasks import backtesting_simulation_consumer
from stock.tasks import chenmin_consumer
from stock.tasks import import_china_stock_consumer
from stock.tasks import influx_consumer
from stock.tasks import stock_flag_sp500_consumer
from stock.tasks import stock_historical_yahoo_consumer
from stock.tasks import stock_monitor_yahoo_consumer
from stock.tasks import stock_monitor_yahoo_consumer2
from stock.tasks import stock_prev_fib_yahoo_consumer
from stock.tasks import stock_prev_month_yahoo_consumer
from stock.tasks import stock_prev_week_yahoo_consumer
from stock.tasks import stock_prev_yahoo_consumer
from stock.utility import JSONEncoder
from stock.utility import MyUtility

sys.path.append(os.path.join(os.path.dirname(__file__), 'jk'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jk.settings")


logger = logging.getLogger('jk')


def populate_sp_500():
    # for s in MyStock.objects.filter(is_sp500=True): s.delete()

    symbols = 'A,AA,AAL,AAPL,ABBV,ABC,ABT,ACE,ACN,ADBE,ADI,ADM,ADP,ADS,ADSK,ADT,AEE,AEP,AES,AET,AFL,AIG,AIV,AIZ,AKAM,ALL,ALLE,ALTR,ALXN,AMAT,AME,AMG,AMGN,AMP,AMT,AMZN,AN,ANTM,AON,APA,APC,APD,APH,ARG,ATI,AVB,AVGO,AVY,AXP,AZO,BA,BAC,BAX,BBBY,BBT,BBY,BCR,BDX,BEN,BF.B,BHI,BIIB,BK,BLK,BLL,BMY,BRCM,BRK.B,BSX,BWA,BXP,C,CA,CAG,CAH,CAM,CAT,CB,CBG,CBS,CCE,CCI,CCL,CELG,CERN,CF,CHK,CHRW,CI,CINF,CL,CLX,CMA,CMCSA,CME,CMG,CMI,CMS,CNP,CNX,COF,COG,COH,COL,COP,COST,CPB,CRM,CSC,CSCO,CSX,CTAS,CTL,CTSH,CTXS,CVC,CVS,CVX,D,DAL,DD,DE,DFS,DG,DGX,DHI,DHR,DIS,DISCA,DISCK,DLPH,DLTR,DNB,DO,DOV,DOW,DPS,DRI,DTE,DTV,DUK,DVA,DVN,EA,EBAY,ECL,ED,EFX,EIX,EL,EMC,EMN,EMR,ENDP,EOG,EQIX,EQR,EQT,ES,ESRX,ESS,ESV,ETFC,ETN,ETR,EW,EXC,EXPD,EXPE,F,FAST,FB,FCX,FDO,FDX,FE,FFIV,FIS,FISV,FITB,FLIR,FLR,FLS,FMC,FOSL,FOXA,FSLR,FTI,FTR,GAS,GCI,GD,GE,GGP,GILD,GIS,GLW,GM,GMCR,GME,GNW,GOOG,GOOGL,GPC,GPS,GRMN,GS,GT,GWW,HAL,HAR,HAS,HBAN,HBI,HCA,HCBK,HCN,HCP,HD,HES,HIG,HOG,HON,HOT,HP,HPQ,HRB,HRL,HRS,HSIC,HSP,HST,HSY,HUM,IBM,ICE,IFF,INTC,INTU,IP,IPG,IR,IRM,ISRG,ITW,IVZ,JCI,JEC,JNJ,JNPR,JOY,JPM,JWN,K,KEY,KIM,KLAC,KMB,KMI,KMX,KO,KORS,KR,KSS,KSU,L,LB,LEG,LEN,LH,LLL,LLTC,LLY,LM,LMT,LNC,LOW,LRCX,LUK,LUV,LVLT,LYB,M,MA,MAC,MAR,MAS,MAT,MCD,MCHP,MCK,MCO,MDLZ,MDT,MET,MHFI,MHK,MJN,MKC,MLM,MMC,MMM,MNK,MNST,MO,MON,MOS,MPC,MRK,MRO,MS,MSFT,MSI,MTB,MU,MUR,MYL,NAVI,NBL,NDAQ,NE,NEE,NEM,NFLX,NFX,NI,NKE,NLSN,NOC,NOV,NRG,NSC,NTAP,NTRS,NUE,NVDA,NWL,NWSA,O,OI,OKE,OMC,ORCL,ORLY,OXY,PAYX,PBCT,PBI,PCAR,PCG,PCL,PCLN,PCP,PDCO,PEG,PEP,PFE,PFG,PG,PGR,PH,PHM,PKI,PLD,PLL,PM,PNC,PNR,PNW,POM,PPG,PPL,PRGO,PRU,PSA,PSX,PVH,PWR,PX,PXD,QCOM,QEP,R,RAI,RCL,REGN,RF,RHI,RHT,RIG,RL,ROK,ROP,ROST,RRC,RSG,RTN,SBUX,SCG,SCHW,SE,SEE,SHW,SIAL,SJM,SLB,SLG,SNA,SNDK,SNI,SO,SPG,SPLS,SRCL,SRE,STI,STJ,STT,STX,STZ,SWK,SWKS,SWN,SYK,SYMC,SYY,T,TAP,TDC,TE,TEL,TGT,THC,TIF,TJX,TMK,TMO,TRIP,TROW,TRV,TSCO,TSN,TSO,TSS,TWC,TWX,TXN,TXT,TYC,UA,UHS,UNH,UNM,UNP,UPS,URBN,URI,USB,UTX,V,VAR,VFC,VIAB,VLO,VMC,VNO,VRSN,VRTX,VTR,VZ,WAT,WBA,WDC,WEC,WFC,WFM,WHR,WM,WMB,WMT,WU,WY,WYN,WYNN,XEC,XEL,XL,XLNX,XOM,XRAY,XRX,XYL,YHOO,YUM,ZION,ZTS,AMAZ,ABNB,VMW'
    for s in symbols.split(','):
        if '.' in s:
            continue
        stock, created = MyStock.objects.get_or_create(symbol=s)


def crawl_stock_prev_yahoo():
    step = 100
    total = 500
    for s in MyStock.objects.filter(is_sp500=True).values_list('symbol', flat=True):
        stock_prev_yahoo_consumer.delay(s)


def crawl_stock_yahoo_spot():
    step = 100
    total = 600
    symbols = MyStock.objects.filter(
        is_sp500=True).values_list('symbol', flat=True)
    for i in xrange(total / step):
        stock_monitor_yahoo_consumer.delay(
            ','.join(symbols[i * step:(i * step + step)]))


def crawl_update_sp500_spot_yahoo():
    """Yahoo! api can take comma delimitered symbols,
    so we batch them 100 per set to save number of queries.
    """
    step = 100
    total = 600
    symbols = MyStock.objects.filter(
        is_sp500=True).values_list('symbol', flat=True)
    logger.debug('Updating S&P 500: %d symbols' % len(symbols))
    for i in xrange(total / step):
        stock_monitor_yahoo_consumer2.delay(
            ','.join(symbols[i * step:(i * step + step)]))


def crawl_update_sp500_historical_yahoo():
    symbols = MyStock.objects.filter(
        is_sp500=True).values_list('symbol', flat=True)

    for s in symbols:
        stock_prev_week_yahoo_consumer.delay(s)
        stock_prev_month_yahoo_consumer.delay(s)
        stock_prev_fib_yahoo_consumer.delay(s)
        stock_historical_yahoo_consumer.delay(s)


def crawler_influx():
    for symbol in list(set(MyStockHistorical.objects.values_list('stock__symbol', flat=True))):
        influx_consumer.delay(symbol)
        print '%s queued' % symbol


def backtest_s1():
    for symbol in list(set(MyStockHistorical.objects.values_list('stock__symbol', flat=True))):
        backtesting_s1_consumer.delay(symbol)


def consumer_daily_return():
    for symbol in MyStock.objects.filter(is_sp500=True).values_list('symbol', flat=True):
        backtesting_daily_return_consumer.delay(symbol)


def consumer_relative_hl():
    for symbol in MyStock.objects.filter(is_sp500=True).values_list('symbol', flat=True):
        backtesting_relative_hl_consumer.delay(symbol)


def consumer_relative_ma():
    for symbol in MyStock.objects.filter(is_sp500=True).values_list('symbol', flat=True):
        backtesting_relative_ma_consumer.delay(symbol)


def dump(qs, outfile_path):
    """
    Takes in a Django queryset and spits out a CSV file.
    Usage::

        >> from utils import dump2csv
        >> from dummy_app.models import *
        >> qs = DummyModel.objects.filter(is_sp500=True)
        >> dump2csv.dump(qs, './data/dump.csv')

    Based on a snippet by zbyte64::

            http://www.djangosnippets.org/snippets/790/

    """
    model = qs.model
    with codecs.open(outfile_path, "w") as temp:
        # writer = csv.writer(open(outfile_path, 'w'))
        writer = csv.writer(temp)

        headers = []
        for field in model._meta.fields:
            headers.append(field.name)
        headers = headers[1:]
        writer.writerow(headers)

        for obj in qs:
            row = []
            for field in headers:
                val = getattr(obj, field)
                if callable(val):
                    val = val()
                if type(val) == unicode:
                    val = val.encode("utf-8")
                row.append(val)
            writer.writerow(row)


def batch_simulation_daily_return(date_range,
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
                # MySimulationCondition is not json-able, using python
                # pickle instead. The downside of this is that we are
                # relying on a python-specif data format.  But it is
                # safe in this context.
                if strategy in [2, 3]:
                    # buy low sell high
                    # Set is_update=True will remove all existing
                    # results first and then rerun all
                    # simulations. This is necessary because SP500 is
                    # gettting new data each day.
                    backtesting_simulation_consumer.delay(
                        cPickle.dumps(condition), is_update=True)
                else:
                    # alpha
                    # Because computing alpha index values are very
                    # time consuming, so we are to skip existing
                    # results to save time. Ideally we should set
                    # is_update=True to recompute from a clean sheet.
                    backtesting_simulation_consumer.delay(
                        cPickle.dumps(condition), is_update=False)


def rerun_existing_simulations(strategy=2):
    total_count = MySimulationCondition.objects.all().count()
    for counter, condition in enumerate(
            MySimulationCondition.objects.filter(strategy=strategy)):
        logger.debug('%s: %d/%d' %
                     (inspect.stack()[1][3], counter, total_count))

        # simulation run
        backtesting_simulation_consumer.delay(
            cPickle.dumps(condition),
            is_update=True)


def main():
    django.setup()

    # tasks
    # populate_sp_500   ()
    # crawl_stock_prev_yahoo()
    # crawl_stock_yahoo_spot()

    # crawler_chenmin()
    # dump_chenmin()
    # crawler_influx()

    # import_chenmin_csv2()
    # crawler_flag_sp500()
    # consumer_oneday_change()
    # import_china_stock_floating_share()
    # import_wind_sector()
    # import_wind_sector_stock()
    # import_wind_sector_index()
    # temp()

    # Pull historical data
    # crawl_update_sp500_historical_yahoo()

    # Pull spot data
    # crawl_update_sp500_spot_yahoo()

    # Compute strategy index values
    # consumer_daily_return()
    # consumer_relative_hl()
    # consumer_relative_ma()

    # simulation
    # generate date range array

    sliding_windows = MyUtility.sliding_windows(
        date(2003, 1, 1),
        date(2005, 1, 1),
        10
    )
    batch_simulation_daily_return(
        date_range=sliding_windows,
        strategies=[2, 3],
        capital=10000,
        per_trade=500
    )

    # back test type 1
    # backtest_s1()

    # rerun simulations
    # rerun_existing_simulations(3)


if __name__ == '__main__':
    main()
