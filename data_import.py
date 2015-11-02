#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,os.path,gc,csv
import lxml.html,codecs
import urllib,urllib2
import re
import simplejson as json
import datetime as dt

# setup Django
import django
sys.path.append(os.path.join(os.path.dirname(__file__), 'jk'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jk.settings")
from django.conf import settings

from django.utils import timezone

# import models
from stock.models import *

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

from stock.tasks import backtesting_s2_consumer
def backtest_s2():
	for symbol in list(set(MyStockHistorical.objects.filter(stock__symbol__startswith="CI00").values_list('stock__symbol',flat=True))):
		backtesting_s2_consumer.delay(symbol)

from stock.tasks import backtesting_s2_rank_consumer
def crawler_s2_rank():
	dates = MyStockHistorical.objects.filter(stock__is_sp500=False,stock__symbol__startswith='CI00').values_list('date_stamp').distinct()
	for d in dates: backtesting_s2_rank_consumer.delay(d[0].isoformat(),ascending=False)

from stock.tasks import backtesting_s3_consumer
def backtest_s3():
	for symbol in list(set(MyStockHistorical.objects.filter(stock__is_sp500=True).values_list('stock__symbol',flat=True))):
	# for symbol in list(set(MyStockHistorical.objects.filter(stock__symbol__startswith="CI00").values_list('stock__symbol',flat=True))):
		backtesting_s3_consumer.delay(symbol)

from stock.tasks import backtesting_s3_rank_consumer
def crawler_s3_rank():
	dates = MyStockHistorical.objects.filter(stock__is_sp500=True).values_list('date_stamp').distinct()
	for d in dates: backtesting_s3_rank_consumer.delay(d[0].isoformat())


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

def import_chenmin_csv2():
	f = '/home/fengxia/Desktop/chenmin/d_data1.csv'
	records = []
	# his = [(x['stock__symbol'],x['date_stamp'].isoformat()) for x in MyStockHistorical.objects.values('stock__symbol','date_stamp').order_by('id')]
	symbols = MyStock.objects.values_list('symbol',flat=True)
	china = []
	with open(f,'rb') as csvfile:
		for cnt, vals in enumerate(csv.reader(csvfile)):
			# print 'processing', cnt

			if len(vals) < 10: 
				print 'wrong length', vals
				raw_input()

			exec_start = time.time()

			if not vals: continue # handle blank lines
			if not re.search('^\d+',vals[0]): continue

			symbol = vals[0].strip()
			# if symbol not in symbols:
			# 	stock,created = MyStock.objects.get_or_create(symbol=symbol)
			# else: stock = MyStock.objects.get(symbol = symbol)

			china.append(symbol)
			continue

			date_stamp = dt(year=int(vals[1][:4]),month=int(vals[1][4:6]),day=int(vals[1][-2:]))

			if (symbol, date_stamp.date()) != his[-1]: continue # we pick up from last break

			if (stock.id,date_stamp.date().isoformat()) in his: continue # we already have these
			else:
				open_p = Decimal(vals[2])
				high_p = Decimal(vals[3])
				low_p = Decimal(vals[4])
				close_p = Decimal(vals[5])
				vol = Decimal(vals[6])
				amount = Decimal(vals[7])*Decimal(10.0)
				adj = Decimal(vals[8])
				status = int(vals[9])
			
				h = MyStockHistorical(
						stock = stock,
						date_stamp = date_stamp,
						open_price = open_p,
						high_price = high_p,
						low_price = low_p,
						close_price = close_p,
						vol = vol,
						amount = amount,
						status = status,

						# adjusted values
						adj_open = open_p * adj,
						adj_high = high_p * adj,
						adj_low = low_p * adj,
						adj_close = close_p * adj,
					)
				records.append(h)
				if len(records) >= 1000:
					MyStockHistorical.objects.bulk_create(records)
					records = []

			print '%d, elapse %f'%(cnt, time.time()-exec_start)
					
		if len(records): MyStockHistorical.objects.bulk_create(records)

	for symbol in set(china):
		stock = MyStock.objects.get(symbol=symbol)
		stock.is_china_stock = True
		stock.save()
		print symbol, 'marked'
from stock.tasks import stock_flag_sp500_consumer
def crawler_flag_sp500():
	stock_flag_sp500_consumer.delay()

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
	#import_chenmin_csv2()	
	#crawler_flag_sp500()
	# backtest_s2()
	# crawler_s2_rank()
	backtest_s3()
	# crawler_s3_rank()

if __name__ == '__main__':
	main()
