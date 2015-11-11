#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,os.path,gc,csv
import lxml.html,codecs
import urllib,urllib2
import re, xlrd, cPickle, time
import simplejson as json
import datetime as dt
from decimal import Decimal
import itertools

# setup Django
import django
sys.path.append(os.path.join(os.path.dirname(__file__), 'jk'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jk.settings")
from django.conf import settings

from django.utils import timezone

# import models
from stock.models import *
from stock.simulations import *
from stock.utility import JSONEncoder

def populate_sp_500():
	# for s in MyStock.objects.filter(is_sp500=True): s.delete()

	symbols = 'A,AA,AAL,AAPL,ABBV,ABC,ABT,ACE,ACN,ADBE,ADI,ADM,ADP,ADS,ADSK,ADT,AEE,AEP,AES,AET,AFL,AIG,AIV,AIZ,AKAM,ALL,ALLE,ALTR,ALXN,AMAT,AME,AMG,AMGN,AMP,AMT,AMZN,AN,ANTM,AON,APA,APC,APD,APH,ARG,ATI,AVB,AVGO,AVY,AXP,AZO,BA,BAC,BAX,BBBY,BBT,BBY,BCR,BDX,BEN,BF.B,BHI,BIIB,BK,BLK,BLL,BMY,BRCM,BRK.B,BSX,BWA,BXP,C,CA,CAG,CAH,CAM,CAT,CB,CBG,CBS,CCE,CCI,CCL,CELG,CERN,CF,CHK,CHRW,CI,CINF,CL,CLX,CMA,CMCSA,CME,CMG,CMI,CMS,CNP,CNX,COF,COG,COH,COL,COP,COST,CPB,CRM,CSC,CSCO,CSX,CTAS,CTL,CTSH,CTXS,CVC,CVS,CVX,D,DAL,DD,DE,DFS,DG,DGX,DHI,DHR,DIS,DISCA,DISCK,DLPH,DLTR,DNB,DO,DOV,DOW,DPS,DRI,DTE,DTV,DUK,DVA,DVN,EA,EBAY,ECL,ED,EFX,EIX,EL,EMC,EMN,EMR,ENDP,EOG,EQIX,EQR,EQT,ES,ESRX,ESS,ESV,ETFC,ETN,ETR,EW,EXC,EXPD,EXPE,F,FAST,FB,FCX,FDO,FDX,FE,FFIV,FIS,FISV,FITB,FLIR,FLR,FLS,FMC,FOSL,FOXA,FSLR,FTI,FTR,GAS,GCI,GD,GE,GGP,GILD,GIS,GLW,GM,GMCR,GME,GNW,GOOG,GOOGL,GPC,GPS,GRMN,GS,GT,GWW,HAL,HAR,HAS,HBAN,HBI,HCA,HCBK,HCN,HCP,HD,HES,HIG,HOG,HON,HOT,HP,HPQ,HRB,HRL,HRS,HSIC,HSP,HST,HSY,HUM,IBM,ICE,IFF,INTC,INTU,IP,IPG,IR,IRM,ISRG,ITW,IVZ,JCI,JEC,JNJ,JNPR,JOY,JPM,JWN,K,KEY,KIM,KLAC,KMB,KMI,KMX,KO,KORS,KR,KSS,KSU,L,LB,LEG,LEN,LH,LLL,LLTC,LLY,LM,LMT,LNC,LOW,LRCX,LUK,LUV,LVLT,LYB,M,MA,MAC,MAR,MAS,MAT,MCD,MCHP,MCK,MCO,MDLZ,MDT,MET,MHFI,MHK,MJN,MKC,MLM,MMC,MMM,MNK,MNST,MO,MON,MOS,MPC,MRK,MRO,MS,MSFT,MSI,MTB,MU,MUR,MYL,NAVI,NBL,NDAQ,NE,NEE,NEM,NFLX,NFX,NI,NKE,NLSN,NOC,NOV,NRG,NSC,NTAP,NTRS,NUE,NVDA,NWL,NWSA,O,OI,OKE,OMC,ORCL,ORLY,OXY,PAYX,PBCT,PBI,PCAR,PCG,PCL,PCLN,PCP,PDCO,PEG,PEP,PFE,PFG,PG,PGR,PH,PHM,PKI,PLD,PLL,PM,PNC,PNR,PNW,POM,PPG,PPL,PRGO,PRU,PSA,PSX,PVH,PWR,PX,PXD,QCOM,QEP,R,RAI,RCL,REGN,RF,RHI,RHT,RIG,RL,ROK,ROP,ROST,RRC,RSG,RTN,SBUX,SCG,SCHW,SE,SEE,SHW,SIAL,SJM,SLB,SLG,SNA,SNDK,SNI,SO,SPG,SPLS,SRCL,SRE,STI,STJ,STT,STX,STZ,SWK,SWKS,SWN,SYK,SYMC,SYY,T,TAP,TDC,TE,TEL,TGT,THC,TIF,TJX,TMK,TMO,TRIP,TROW,TRV,TSCO,TSN,TSO,TSS,TWC,TWX,TXN,TXT,TYC,UA,UHS,UNH,UNM,UNP,UPS,URBN,URI,USB,UTX,V,VAR,VFC,VIAB,VLO,VMC,VNO,VRSN,VRTX,VTR,VZ,WAT,WBA,WDC,WEC,WFC,WFM,WHR,WM,WMB,WMT,WU,WY,WYN,WYNN,XEC,XEL,XL,XLNX,XOM,XRAY,XRX,XYL,YHOO,YUM,ZION,ZTS'
	for s in symbols.split(','):
		if '.' in s: continue
		stock,created = MyStock.objects.get_or_create(symbol=s)	

from stock.tasks import stock_prev_yahoo_consumer
def crawl_stock_prev_yahoo():
	step = 100
	total = 500
	for s in MyStock.objects.filter(is_sp500=True).values_list('symbol',flat=True):
		stock_prev_yahoo_consumer.delay(s)

from stock.tasks import stock_monitor_yahoo_consumer
def crawl_stock_yahoo_spot():
	step = 100
	total = 500
	symbols = MyStock.objects.filter(is_sp500=True).values_list('symbol',flat=True)
	for i in xrange(total/step):	
		stock_monitor_yahoo_consumer.delay(','.join(symbols[i*step:(i*step+step)]))

from stock.tasks import stock_monitor_yahoo_consumer2
def crawl_stock_yahoo_spot2():
	step = 100
	total = 500
	symbols = MyStock.objects.filter(is_sp500=True).values_list('symbol',flat=True)
	for i in xrange(total/step):	
		stock_monitor_yahoo_consumer2.delay(','.join(symbols[i*step:(i*step+step)]))


from stock.tasks import stock_prev_week_yahoo_consumer,stock_prev_month_yahoo_consumer,stock_prev_fib_yahoo_consumer,stock_historical_yahoo_consumer
def crawl_stock_prev_yahoo2():
	symbols = MyStock.objects.filter(is_sp500=True).values_list('symbol',flat=True)
	for s in symbols:	
		stock_prev_week_yahoo_consumer.delay(s)
		stock_prev_month_yahoo_consumer.delay(s)
		stock_prev_fib_yahoo_consumer.delay(s)
		stock_historical_yahoo_consumer.delay(s)

from stock.tasks import chenmin_consumer
def crawler_chenmin():
	root = '/home/fengxia/Downloads/chenmin'
	files = filter(lambda x: '.xls' in x, os.listdir(root))	
	for f in [os.path.join(root,f) for f in files]:
		chenmin_consumer.delay(f)

from stock.tasks import influx_consumer
from influxdb.influxdb08 import InfluxDBClient
def crawler_influx():
	for symbol in list(set(MyStockHistorical.objects.values_list('stock__symbol',flat=True))):
		influx_consumer.delay(symbol)
		print '%s queued'%symbol

from stock.tasks import backtesting_s1_consumer
def backtest_s1():
	for symbol in list(set(MyStockHistorical.objects.values_list('stock__symbol',flat=True))):
		backtesting_s1_onsumer.delay(symbol)

from stock.tasks import backtesting_daily_return_consumer
def consumer_daily_return():
	for symbol in MyStock.objects.filter(symbol__startswith = '8821').values_list('symbol',flat=True):
		backtesting_daily_return_consumer.delay(symbol)

from stock.tasks import backtesting_relative_hl_consumer
def consumer_relative_hl():
	for symbol in MyStock.objects.filter(symbol__startswith = '8821').values_list('symbol',flat=True):
		backtesting_relative_hl_consumer.delay(symbol)

from stock.tasks import backtesting_relative_ma_consumer
def consumer_relative_ma():
	for symbol in MyStock.objects.values_list('symbol',flat=True):
		backtesting_relative_ma_consumer.delay(symbol)

import csv
from django.db.models.loading import get_model
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

def dump_chenmin():
	root = '/home/fengxia/Desktop/chenmin'
	total = len(MyChenmin.objects.values_list('symbol',flat=True).distinct())

	for idx, symbol in enumerate(MyChenmin.objects.values_list('symbol',flat=True).distinct()):
		dump(MyChenmin.objects.filter(symbol=symbol).order_by('executed_on'),os.path.join(root,symbol+'.csv'))
		print '%d/%d'%(idx, total), symbol

def import_chenmin_csv():
	root = '/home/fengxia/Desktop/chenmin/alpha'
	for f in os.listdir(root):
		symbol,ext = os.path.splitext(os.path.basename(f))
		stock,created = MyStock.objects.get_or_create(symbol=symbol)
		his = [x.isoformat() for x in MyStockHistorical.objects.filter(stock=stock).values_list('date_stamp',flat=True)]
		records = []

		with open(os.path.join(root,f),'rb') as csvfile:
			for cnt, vals in enumerate(csv.reader(csvfile)):
				if not vals: continue # handle blank lines

				# some time stamp is in form of "x/x/x", normalized to "x-x-x" format
				vals[0] = vals[0].replace('/','-')
				if len(vals) != 6: 
					print 'error in %s' % symbol
					print cnt, vals
					raw_input()
				elif '-' not in vals[0]: continue # skip these title lines

				stamp = [int(v) for v in vals[0].split('-')]
				date_stamp = dt(year=stamp[0],month=stamp[1],day=stamp[2])

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
		if len(records): MyStockHistorical.objects.bulk_create(records)

		# persist
		print '[%s] complete'%symbol					

from stock.tasks import import_china_stock_consumer
def import_chenmin_csv2():
	f = '/home/fengxia/Desktop/chenmin/d_data1.csv'
	records = []
	for china in MyStock.objects.filter(is_china_stock=True):
		MyStockHistorical.objects.filter(stock=china).delete()

	historicals = {}
	with open(f,'rb') as csvfile:
		for cnt, vals in enumerate(csv.reader(csvfile)):
			if not vals: continue # handle blank lines
			if not re.search('^\d+',vals[0]): continue

			symbol = vals[0].strip()
			if symbol in historicals: historicals[symbol].append(vals)
			else: historicals[symbol] = [vals]

	for symbol, val_list in historicals.iteritems():
		import_china_stock_consumer.delay(symbol,val_list)

from stock.tasks import stock_flag_sp500_consumer
def crawler_flag_sp500():
	stock_flag_sp500_consumer.delay()

def import_china_stock_floating_share():
	f = u'/home/fengxia/Desktop/chenmin/study/All_Stock_流通股本.csv'
	records = []

	with open(f,'rb') as csvfile:
		for cnt, vals in enumerate(csv.reader(csvfile)):
			if '.' not in vals[0]: continue

			symbol = vals[0].split('.')[0]
			floating_share = float(vals[-1])/1000000.0
			print symbol, floating_share

			stock = MyStock.objects.get(symbol=symbol)
			stock.floating_share = floating_share
			stock.save()

def import_wind_sector():
	f = u'/home/fengxia/Desktop/chenmin/sector/sector.xls'
	workbook = xlrd.open_workbook(f)
	sheet = workbook.sheet_by_index(0)
	s1 = s2 = s3 = s4 = None

	for row_idx in range(4,274):
		level_1 = sheet.cell_value(row_idx,0)
		if level_1: level_1 = str(int(level_1))
		level_1_desp = sheet.cell_value(row_idx,1).strip()

		level_2 = sheet.cell_value(row_idx,2)
		if level_2: level_2 = str(int(level_2))
		level_2_desp = sheet.cell_value(row_idx,3).strip()

		level_3 = sheet.cell_value(row_idx,4)
		if level_3: level_3 = str(int(level_3))
		level_3_desp = sheet.cell_value(row_idx,5).strip()

		level_4 = sheet.cell_value(row_idx,6)
		if level_4: level_4 = str(int(level_4))
		level_4_desp = sheet.cell_value(row_idx,7).strip()

		if not level_4_desp: continue # blank cell

		if level_1 and level_1_desp:
			s1 = MySector(
				code = level_1,
				name = level_1_desp,
				source = 'wind',
			)
			s1.save()
			print 'level 1 %s created' % level_1

		if level_2 and level_2_desp and s1:
			s2 = MySector(
				code = level_2,
				name = level_2_desp,
				source = 'wind',
				parent = s1
			)
			s2.save()
			print 'level 2 %s created' % level_2

		if level_3 and level_3_desp and s2:
			s3 = MySector(
				code = level_3,
				name = level_3_desp,
				source = 'wind',
				parent = s2
			)
			s3.save()
			print 'level 3 %s created' % level_3

		# level-4 description line
		if s4 and level_4_desp:
			s4.description = level_4_desp
			s4.save()
			print 'level 4 description saved'

		# level-4 name line
		if level_4_desp and level_4 and s3:
			s4 = MySector(
				code = level_4,
				name = level_4_desp,
				source = 'wind',
				parent = s3
			)
			s4.save()
			print 'level 4 %s created' % level_4

def import_wind_sector_stock():
	root = '/home/fengxia/Desktop/chenmin/sector/wind'
	missing_sectors = []
	missing_symbols = []
	for f in os.listdir(root):
		sector,ext = os.path.splitext(os.path.basename(f))
		try:
			sector = MySector.objects.get(code=sector)
		except:
			missing_sectors.append(sector)
			continue

		with open(os.path.join(root,f),'rb') as csvfile:
			for cnt, vals in enumerate(csv.reader(csvfile)):
				symbol = vals[2].split('.')[0]
				if not re.search('^\d+',symbol): continue
				try:
					stock = MyStock.objects.get(symbol=symbol)
					sector.stocks.add(stock)
					print 'sector %s add stock %s'%(sector.name,stock.symbol)
				except: missing_symbols.append(symbol)

	print 'missing sectors', missing_sectors
	print 'missing symbols:', missing_symbols

def import_wind_sector_index():
	sectors = {
		'882112':'3030',
		'882111':'3020',
		'882116':'4020',
		'882119':'4510',
		'882101':'1510',
		'882117':'4030',
		'882121':'4530',
		'882108':'2540',
		'882110':'2550',
		'882115':'4010',
		'882100':'1010',
		'882118':'4040',
		'882103':'2020',
		'882120':'4520',
		'882106':'2520',
		'882113':'3510',
		'882104':'2030',
		'882102':'2010',
		'882105':'2510',
		'882107':'2530',
		'882114':'3520',
		'882123':'5510',
		'882122':'5010',
		'882109':'3010',	
	}
	f = u'/home/fengxia/Desktop/chenmin/sector/Wind_index_historical_2005-2015.xlsx'
	workbook = xlrd.open_workbook(f)
	for sheet in workbook.sheets():
		symbol = sheet.name.strip()
		stock,created = MyStock.objects.get_or_create(symbol=symbol)
		print 'stock symbol', symbol

		print 'sector code', sectors[symbol]
		sector = MySector.objects.get(code = sectors[symbol])
		sector.stocks.add(stock)

		records = []
		print 'rows', sheet.nrows
		for r_idx in range(sheet.nrows):
			vals = sheet.row_values(r_idx)[:6]
			if reduce(lambda x,y: x or y, map(lambda x: not x,vals[:-1])): continue
			try: int(vals[0]) # for date stamp line, vals[0] is a floating number
			except: continue

			date_stamp = xlrd.xldate.xldate_as_datetime(vals[0],workbook.datemode)
			h = MyStockHistorical(
					stock=stock,
					date_stamp=date_stamp,
					open_price=vals[1],
					high_price=vals[2],
					low_price=vals[3],
					close_price=vals[4],
					vol=vals[5]/1000,
				)
			records.append(h)
		MyStockHistorical.objects.bulk_create(records)
		# print 'done', symbol, len(records)

from stock.tasks import backtesting_simulation_consumer
def batch_simulation_daily_return():
	sources = [2,3,5]
	strategies = [1,2]
	strategy_values = [1,2,3]

	# get 8211 related sectors
	stock_8211 = MyStock.objects.filter(symbol__startswith="8821")
	sectors = [None]+reduce(lambda x,y:x+y, [list(s.mysector_set.all()) for s in stock_8211])
	
	start = ['2010-01-01','2015-01-01']
	end = ['2016-01-01']
	# start = ['2015-01-01']
	# end = ['2015-01-10']

	step = 25
	conditions = []
	for (source,strategy,strategy_value,start,end,sector) in itertools.product(sources,strategies,strategy_values,start,end,sectors):
		# we only try strategy 2 with source 1
		if strategy == 2 and source != 1: continue

		# we only try strategy 5 with sector
		if sector and source != 5: continue

		print source,strategy,strategy_value,start,end,sector

		# cutoffs have different meanings based on strategy
		if strategy == 1:
			buy_cutoff = range(0,100,25)
			sell_cutoff = [b+25 for b in buy_cutoff]
			cutoffs = zip(buy_cutoff,sell_cutoff)
		elif strategy == 2:
			cutoffs = itertools.product([1,5,10],[1,5,10])

		for (buy_cutoff,sell_cutoff) in cutoffs:
			condition,created = MySimulationCondition.objects.get_or_create(
				data_source = source,
				sector = sector,
				data_sort = 1, # descending
				strategy = strategy,
				strategy_value = strategy_value,
				start = start,
				end = end,
				capital = 100000,
				per_trade = 10000,
				buy_cutoff = buy_cutoff,
				sell_cutoff = sell_cutoff
			)
			conditions.append(condition)

	for condition in conditions:
		backtesting_simulation_consumer.delay(cPickle.dumps(condition))

def temp():
	s = '3010'
	stocks = []
	for sector in MySector.objects.filter(code__startswith=s):
		for stock in sector.stocks.all():
			if stock.symbol.startswith('8821'): continue
			else: stocks.append(stock)
	print stocks

def main():
	django.setup()

	# tasks
	# populate_sp_500	()
	# crawl_stock_prev_yahoo()
	# crawl_stock_yahoo_spot2()	
	# crawl_stock_prev_yahoo2()

	# crawl_stock_yahoo_spot()

	# crawler_chenmin()
	# dump_chenmin()
	# crawler_influx()
	#backtest_1()
	# import_chenmin_csv2()	
	#crawler_flag_sp500()
	# consumer_oneday_change()
	# import_china_stock_floating_share()
	# import_wind_sector()
	# import_wind_sector_stock()
	# import_wind_sector_index()
	batch_simulation_daily_return()
	# temp()

	'''
	Compute strategy index values
	'''
	# consumer_daily_return()
	# consumer_relative_hl()
	# consumer_relative_ma()

if __name__ == '__main__':
	main()
