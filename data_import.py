#!/usr/bin/python  
# -*- coding: utf-8 -*- 
import sys,time,os,os.path,gc,csv
import lxml.html,codecs
import urllib,urllib2
import re
import simplejson as json

# setup Django
import django
sys.path.append(os.path.join(os.path.dirname(__file__), 'jk'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jk.settings")
from django.conf import settings

from django.utils import timezone

# import models
from stock.models import *

def populate_sp_500():
	# for s in MyStock.objects.all(): s.delete()

	symbols = 'A,AA,AAL,AAPL,ABBV,ABC,ABT,ACE,ACN,ADBE,ADI,ADM,ADP,ADS,ADSK,ADT,AEE,AEP,AES,AET,AFL,AIG,AIV,AIZ,AKAM,ALL,ALLE,ALTR,ALXN,AMAT,AME,AMG,AMGN,AMP,AMT,AMZN,AN,ANTM,AON,APA,APC,APD,APH,ARG,ATI,AVB,AVGO,AVY,AXP,AZO,BA,BAC,BAX,BBBY,BBT,BBY,BCR,BDX,BEN,BF.B,BHI,BIIB,BK,BLK,BLL,BMY,BRCM,BRK.B,BSX,BWA,BXP,C,CA,CAG,CAH,CAM,CAT,CB,CBG,CBS,CCE,CCI,CCL,CELG,CERN,CF,CHK,CHRW,CI,CINF,CL,CLX,CMA,CMCSA,CME,CMG,CMI,CMS,CNP,CNX,COF,COG,COH,COL,COP,COST,CPB,CRM,CSC,CSCO,CSX,CTAS,CTL,CTSH,CTXS,CVC,CVS,CVX,D,DAL,DD,DE,DFS,DG,DGX,DHI,DHR,DIS,DISCA,DISCK,DLPH,DLTR,DNB,DO,DOV,DOW,DPS,DRI,DTE,DTV,DUK,DVA,DVN,EA,EBAY,ECL,ED,EFX,EIX,EL,EMC,EMN,EMR,ENDP,EOG,EQIX,EQR,EQT,ES,ESRX,ESS,ESV,ETFC,ETN,ETR,EW,EXC,EXPD,EXPE,F,FAST,FB,FCX,FDO,FDX,FE,FFIV,FIS,FISV,FITB,FLIR,FLR,FLS,FMC,FOSL,FOXA,FSLR,FTI,FTR,GAS,GCI,GD,GE,GGP,GILD,GIS,GLW,GM,GMCR,GME,GNW,GOOG,GOOGL,GPC,GPS,GRMN,GS,GT,GWW,HAL,HAR,HAS,HBAN,HBI,HCA,HCBK,HCN,HCP,HD,HES,HIG,HOG,HON,HOT,HP,HPQ,HRB,HRL,HRS,HSIC,HSP,HST,HSY,HUM,IBM,ICE,IFF,INTC,INTU,IP,IPG,IR,IRM,ISRG,ITW,IVZ,JCI,JEC,JNJ,JNPR,JOY,JPM,JWN,K,KEY,KIM,KLAC,KMB,KMI,KMX,KO,KORS,KR,KSS,KSU,L,LB,LEG,LEN,LH,LLL,LLTC,LLY,LM,LMT,LNC,LOW,LRCX,LUK,LUV,LVLT,LYB,M,MA,MAC,MAR,MAS,MAT,MCD,MCHP,MCK,MCO,MDLZ,MDT,MET,MHFI,MHK,MJN,MKC,MLM,MMC,MMM,MNK,MNST,MO,MON,MOS,MPC,MRK,MRO,MS,MSFT,MSI,MTB,MU,MUR,MYL,NAVI,NBL,NDAQ,NE,NEE,NEM,NFLX,NFX,NI,NKE,NLSN,NOC,NOV,NRG,NSC,NTAP,NTRS,NUE,NVDA,NWL,NWSA,O,OI,OKE,OMC,ORCL,ORLY,OXY,PAYX,PBCT,PBI,PCAR,PCG,PCL,PCLN,PCP,PDCO,PEG,PEP,PFE,PFG,PG,PGR,PH,PHM,PKI,PLD,PLL,PM,PNC,PNR,PNW,POM,PPG,PPL,PRGO,PRU,PSA,PSX,PVH,PWR,PX,PXD,QCOM,QEP,R,RAI,RCL,REGN,RF,RHI,RHT,RIG,RL,ROK,ROP,ROST,RRC,RSG,RTN,SBUX,SCG,SCHW,SE,SEE,SHW,SIAL,SJM,SLB,SLG,SNA,SNDK,SNI,SO,SPG,SPLS,SRCL,SRE,STI,STJ,STT,STX,STZ,SWK,SWKS,SWN,SYK,SYMC,SYY,T,TAP,TDC,TE,TEL,TGT,THC,TIF,TJX,TMK,TMO,TRIP,TROW,TRV,TSCO,TSN,TSO,TSS,TWC,TWX,TXN,TXT,TYC,UA,UHS,UNH,UNM,UNP,UPS,URBN,URI,USB,UTX,V,VAR,VFC,VIAB,VLO,VMC,VNO,VRSN,VRTX,VTR,VZ,WAT,WBA,WDC,WEC,WFC,WFM,WHR,WM,WMB,WMT,WU,WY,WYN,WYNN,XEC,XEL,XL,XLNX,XOM,XRAY,XRX,XYL,YHOO,YUM,ZION,ZTS'
	for s in symbols.split(','):
		if '.' in s: continue
		stock,created = MyStock.objects.get_or_create(symbol=s)	

from stock.tasks import stock_prev_yahoo_consumer
def crawl_stock_prev_yahoo():
	step = 100
	total = 500
	for s in MyStock.objects.all().values_list('symbol',flat=True):
		stock_prev_yahoo_consumer.delay(s)

from stock.tasks import stock_monitor_yahoo_consumer
def crawl_stock_yahoo_spot():
	step = 100
	total = 500
	symbols = MyStock.objects.all().values_list('symbol',flat=True)
	for i in xrange(total/step):	
		stock_monitor_yahoo_consumer.delay(','.join(symbols[i*step:(i*step+step)]))

from stock.tasks import stock_monitor_yahoo_consumer2
def crawl_stock_yahoo_spot2():
	step = 100
	total = 500
	symbols = MyStock.objects.all().values_list('symbol',flat=True)
	for i in xrange(total/step):	
		stock_monitor_yahoo_consumer2.delay(','.join(symbols[i*step:(i*step+step)]))


from stock.tasks import stock_prev_week_yahoo_consumer,stock_prev_month_yahoo_consumer,stock_prev_fib_yahoo_consumer,stock_historical_yahoo_consumer
def crawl_stock_prev_yahoo2():
	symbols = MyStock.objects.all().values_list('symbol',flat=True)
	for s in symbols:	
		# stock_prev_week_yahoo_consumer.delay(s)
		# stock_prev_month_yahoo_consumer.delay(s)
		# stock_prev_fib_yahoo_consumer.delay(s)
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

from stock.tasks import backtesting_consumer
def backtest_1():
	for symbol in list(set(MyStockHistorical.objects.values_list('stock__symbol',flat=True))):
		backtesting_consumer.delay(symbol)

import csv
from django.db.models.loading import get_model
def dump(qs, outfile_path):
	"""
	Takes in a Django queryset and spits out a CSV file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
	
	Usage::
	
		>> from utils import dump2csv
		>> from dummy_app.models import *
		>> qs = DummyModel.objects.all()
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

def main():
	django.setup()

	# tasks
	# populate_sp_500	()
	# crawl_stock_prev_yahoo()
	crawl_stock_prev_yahoo2()

	# crawl_stock_yahoo_spot()
	#crawl_stock_yahoo_spot2()

	# crawler_chenmin()
	# dump_chenmin()
	# crawler_influx()
	#backtest_1()

if __name__ == '__main__':
	main()
