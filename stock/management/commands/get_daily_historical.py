import os
import os.path
import sys
from datetime import date
from itertools import chain

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date

from stock.models import MyStock, MyStockHistorical
from stock.tasks import stock_historical_yahoo_consumer

SYMBOLS = "A,AA,AAL,AAPL,ABBV,ABC,ABT,ACE,ACN,ADBE,ADI,ADM,ADP,ADS,ADSK,ADT,AEE,AEP,AES,AET,AFL,AIG,AIV,AIZ,AKAM,ALL,ALLE,ALTR,ALXN,AMAT,AME,AMG,AMGN,AMP,AMT,AMZN,AN,ANTM,AON,APA,APC,APD,APH,ARG,ATI,AVB,AVGO,AVY,AXP,AZO,BA,BAC,BAX,BBBY,BBT,BBY,BCR,BDX,BEN,BF.B,BHI,BIIB,BK,BLK,BLL,BMY,BRCM,BRK.B,BSX,BWA,BXP,C,CA,CAG,CAH,CAM,CAT,CB,CBG,CBS,CCE,CCI,CCL,CELG,CERN,CF,CHK,CHRW,CI,CINF,CL,CLX,CMA,CMCSA,CME,CMG,CMI,CMS,CNP,CNX,COF,COG,COH,COL,COP,COST,CPB,CRM,CSC,CSCO,CSX,CTAS,CTL,CTSH,CTXS,CVC,CVS,CVX,D,DAL,DD,DE,DFS,DG,DGX,DHI,DHR,DIS,DISCA,DISCK,DLPH,DLTR,DNB,DO,DOV,DOW,DPS,DRI,DTE,DTV,DUK,DVA,DVN,EA,EBAY,ECL,ED,EFX,EIX,EL,EMC,EMN,EMR,ENDP,EOG,EQIX,EQR,EQT,ES,ESRX,ESS,ESV,ETFC,ETN,ETR,EW,EXC,EXPD,EXPE,F,FAST,FB,FCX,FDO,FDX,FE,FFIV,FIS,FISV,FITB,FLIR,FLR,FLS,FMC,FOSL,FOXA,FSLR,FTI,FTR,GAS,GCI,GD,GE,GGP,GILD,GIS,GLW,GM,GMCR,GME,GNW,GOOG,GOOGL,GPC,GPS,GRMN,GS,GT,GWW,HAL,HAR,HAS,HBAN,HBI,HCA,HCBK,HCN,HCP,HD,HES,HIG,HOG,HON,HOT,HP,HPQ,HRB,HRL,HRS,HSIC,HSP,HST,HSY,HUM,IBM,ICE,IFF,INTC,INTU,IP,IPG,IR,IRM,ISRG,ITW,IVZ,JCI,JEC,JNJ,JNPR,JOY,JPM,JWN,K,KEY,KIM,KLAC,KMB,KMI,KMX,KO,KORS,KR,KSS,KSU,L,LB,LEG,LEN,LH,LLL,LLTC,LLY,LM,LMT,LNC,LOW,LRCX,LUK,LUV,LVLT,LYB,M,MA,MAC,MAR,MAS,MAT,MCD,MCHP,MCK,MCO,MDLZ,MDT,MET,MHFI,MHK,MJN,MKC,MLM,MMC,MMM,MNK,MNST,MO,MON,MOS,MPC,MRK,MRO,MS,MSFT,MSI,MTB,MU,MUR,MYL,NAVI,NBL,NDAQ,NE,NEE,NEM,NFLX,NFX,NI,NKE,NLSN,NOC,NOV,NRG,NSC,NTAP,NTRS,NUE,NVDA,NWL,NWSA,O,OI,OKE,OMC,ORCL,ORLY,OXY,PAYX,PBCT,PBI,PCAR,PCG,PCL,PCLN,PCP,PDCO,PEG,PEP,PFE,PFG,PG,PGR,PH,PHM,PKI,PLD,PLL,PM,PNC,PNR,PNW,POM,PPG,PPL,PRGO,PRU,PSA,PSX,PVH,PWR,PX,PXD,QCOM,QEP,R,RAI,RCL,REGN,RF,RHI,RHT,RIG,RL,ROK,ROP,ROST,RRC,RSG,RTN,SBUX,SCG,SCHW,SE,SEE,SHW,SIAL,SJM,SLB,SLG,SNA,SNDK,SNI,SO,SPG,SPLS,SRCL,SRE,STI,STJ,STT,STX,STZ,SWK,SWKS,SWN,SYK,SYMC,SYY,T,TAP,TDC,TE,TEL,TGT,THC,TIF,TJX,TMK,TMO,TRIP,TROW,TRV,TSCO,TSN,TSO,TSS,TWC,TWX,TXN,TXT,TYC,UA,UHS,UNH,UNM,UNP,UPS,URBN,URI,USB,UTX,V,VAR,VFC,VIAB,VLO,VMC,VNO,VRSN,VRTX,VTR,VZ,WAT,WBA,WDC,WEC,WFC,WFM,WHR,WM,WMB,WMT,WU,WY,WYN,WYNN,XEC,XEL,XL,XLNX,XOM,XRAY,XRX,XYL,YHOO,YUM,ZION,ZTS,AMAZ,ABNB,VMW,VOO,GSPC"


class Command(BaseCommand):
    help = "Get Yahoo! daily historical data"

    def add_arguments(self, parser):
        parser.add_argument("symbol", help="Stock symbol")

        # Named (optional) arguments
        parser.add_argument(
            "--csv", action="store_true", help="Dump history data to CSV"
        )
        parser.add_argument(
            "--dest", default="./csv", help="Path to put dumped data file"
        )

    def handle(self, *args, **options):
        self.stdout.write(os.path.dirname(__file__), ending="")

        symbol = options["symbol"]

        if options["csv"]:
            dest = options["dest"]
            if symbol == "all":
                for s in SYMBOLS.split(","):
                    self._dump(dest, s)
            else:
                self._dump(dest, symbol)
        else:
            if symbol == "all":
                for s in SYMBOLS.split(","):
                    stock_historical_yahoo_consumer.delay(s)
            else:
                stock_historical_yahoo_consumer.delay(symbol)

    def _dump(self, dest, symbol):
        header = "Date,Open,High,Low,Close,Adj Close,Volume"
        with open("{}/{}.csv".format(dest, symbol), "w") as f:
            data = [header]

            try:
                stock = get_object_or_404(symbol=symbol)
            except Http404:
                # something is seriously wrong!
                return

            historicals = MyStockHistorical.objects.filter(stock=stock).order_by(
                "date_stamp"
            )
            for h in historicals:
                data.append(
                    ",".join(
                        map(
                            lambda x: str(x),
                            [
                                h.date_stamp.strftime("%Y-%m-%d"),
                                h.open_price,
                                h.high_price,
                                h.low_price,
                                h.close_price,
                                h.adj_close,
                                # vol is saved in thousands
                                int(h.vol * 1000),
                            ],
                        )
                    )
                )
            f.write("\n".join(data))
