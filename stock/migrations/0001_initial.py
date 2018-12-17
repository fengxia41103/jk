# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('name', models.CharField(default=b'default name', max_length=64, verbose_name='\u9644\u4ef6\u540d\u79f0')),
                ('description', models.CharField(default=b'default description', max_length=64, verbose_name='\u9644\u4ef6\u63cf\u8ff0')),
                ('file', models.FileField(help_text='\u9644\u4ef6', upload_to=b'%Y/%m/%d', verbose_name='\u9644\u4ef6')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('created_by', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, blank=True, help_text=b'', null=True, verbose_name='\u521b\u5efa\u7528\u6237')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyPosition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('position', models.DecimalField(verbose_name='We paid', max_digits=20, decimal_places=4)),
                ('vol', models.DecimalField(default=0, verbose_name='Trade vol', max_digits=20, decimal_places=4)),
                ('is_open', models.BooleanField(default=True, verbose_name='Is position open')),
                ('last_updated_on', models.DateTimeField(auto_now=True)),
                ('close_position', models.DecimalField(default=0.0, verbose_name='We closed at', max_digits=20, decimal_places=3)),
                ('open_date', models.DateField(null=True, verbose_name='Position open date', blank=True)),
                ('close_date', models.DateField(default=None, null=True, verbose_name='Position close date', blank=True)),
                ('life_in_days', models.IntegerField(default=0, verbose_name='Life in days')),
                ('gain', models.DecimalField(default=0.0, verbose_name='Gain', max_digits=20, decimal_places=3)),
                ('cost', models.DecimalField(default=0.0, verbose_name='Cost', max_digits=20, decimal_places=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySimulationCondition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_source', models.IntegerField(default=1, choices=[(1, b'S&P500')])),
                ('strategy', models.IntegerField(default=1, choices=[(1, b'S1 (by ranking)'), (2, b'S2 (buy low sell high)'), (3, b'S3 (buy high sell low)')])),
                ('strategy_value', models.IntegerField(default=1, verbose_name='Strategy value', choices=[(b'sma', b'simple moving average'), (b'ema', b'exponential moving average'), (b'wma', b'weighted moving average'), (b'dema', b'double exponential moving average'), (b'tema', b'triple exponential moving average'), (b'trima', b'triangular moving average'), (b'kama', b'Kaufman adaptive moving average'), (b'mama', b'MESA adaptive moving average'), (b't3', b'triple exponential moving average'), (b'macd', b'moving average convergence / divergence'), (b'macdext', b'moving average convergence / divergence values with controllable moving average type'), (b'stoch', b'stochastic oscillator'), (b'stochf', b'stochastic fast'), (b'rsi', b'relative strength index'), (b'stochrsi', b'stochastic relative strength index'), (b'willr', b"Williams' %R"), (b'adx', b'average directional movement index'), (b'adxr', b'average directional movement index rating'), (b'apo', b'absolute price oscillator'), (b'ppo', b'percentage price oscillator'), (b'mom', b'momentum'), (b'bop', b'balance of power'), (b'cci', b'commodity channel index'), (b'cmo', b'Chande momentum oscillator'), (b'roc', b'rate of change'), (b'rocr', b'rate of change ratio'), (b'aroon', b'Aroon'), (b'aroonosc', b'Aroon oscillator'), (b'mfi', b'money flow index'), (b'trix', b'1-day rate of change of a triple smooth exponential moving average'), (b'ultosc', b'ultimate oscillator'), (b'dx', b'directional movement index'), (b'minus_di', b'minus directional indicator'), (b'plus_di', b'plus directional indicator'), (b'minus_dm', b'minus directional movement'), (b'plus_dm', b'plus directional movement'), (b'bbands', b'Bollinger bands'), (b'midpoint', b'MIDPOINT = (highest value + lowest value)/2'), (b'midprice', b'MIDPRICE = (highest high + lowest low)/2'), (b'sar', b'parabolic SAR'), (b'trange', b'true range'), (b'atr', b'average true range'), (b'natr', b'normalized average true range'), (b'ad', b'Chaikin A/D line'), (b'adosc', b'Chaikin A/D oscillator'), (b'obv', b'balance volume'), (b'ht_trendline', b'Hilbert transform, instantaneous trendline'), (b'ht_sine', b'Hilbert transform, sine wave'), (b'ht_trendmode', b'Hilbert transform, trend vs cycle mode'), (b'ht_dcperiod', b'Hilbert transform, dominant cycle period'), (b'ht_dcphase', b'Hilbert transform, dominant cycle phase'), (b'ht_phasor', b'Hilbert transform, phasor components')])),
                ('data_sort', models.IntegerField(default=2, verbose_name='Sort order', choices=[(0, b'ascending'), (1, b'descending')])),
                ('start', models.DateField(default=b'2014-01-01', verbose_name='Start date')),
                ('end', models.DateField(default=b'2014-01-10', verbose_name='End date')),
                ('capital', models.IntegerField(default=100000, verbose_name='Starting cash')),
                ('per_trade', models.IntegerField(default=10000, verbose_name='Per trade amount')),
                ('buy_cutoff', models.IntegerField(default=25, verbose_name=b'Buy cutoff (%)', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
                ('sell_cutoff', models.IntegerField(default=75, verbose_name=b'Sell cutoff (%)', validators=[django.core.validators.MaxValueValidator(100), django.core.validators.MinValueValidator(0)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MySimulationSnapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('on_date', models.DateField(default=b'2014-01-01', verbose_name='Snapshot date')),
                ('cash', models.DecimalField(default=0, verbose_name='Cash', max_digits=20, decimal_places=4)),
                ('equity', models.DecimalField(default=0, verbose_name='Equity', max_digits=20, decimal_places=4)),
                ('asset', models.DecimalField(default=0, verbose_name='Asset', max_digits=20, decimal_places=4)),
                ('gain_from_holding', models.DecimalField(default=0, verbose_name='Gain from holding', max_digits=20, decimal_places=4)),
                ('gain_from_exit', models.DecimalField(default=0, verbose_name='Gain from exit', max_digits=20, decimal_places=4)),
                ('asset_gain_pcnt', models.FloatField(default=0, help_text='This measures asset return in pcnt comparing to previous day', verbose_name='Asset gain from previous day')),
                ('asset_gain_pcnt_t0', models.FloatField(default=0, help_text="This measures asset return in pcnt comparing to T0's", verbose_name='Asset gain from T0')),
                ('simulation', models.ForeignKey(to='stock.MySimulationCondition')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyStock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company_name', models.CharField(max_length=128, null=True, verbose_name='Company name', blank=True)),
                ('symbol', models.CharField(max_length=8, verbose_name='Stock symbol')),
                ('sector', models.CharField(default=b'unknown', max_length=64, verbose_name='Sector name')),
                ('is_sp500', models.BooleanField(default=False, verbose_name='Is a SP500 stock')),
                ('is_composite', models.BooleanField(default=False, help_text='Composite is a derived value from basket of stocks', verbose_name='Is a composite stock')),
                ('is_index', models.BooleanField(default=False, help_text='Index is a derived value from basket of stocks', verbose_name='Is an index')),
                ('prev_close', models.DecimalField(default=0.0, verbose_name='Prev day closing price', max_digits=20, decimal_places=5)),
                ('prev_open', models.DecimalField(default=0.0, verbose_name='Prev day opening price', max_digits=20, decimal_places=5)),
                ('prev_high', models.DecimalField(default=0.0, verbose_name='Prev day highest price', max_digits=20, decimal_places=5)),
                ('prev_low', models.DecimalField(default=0.0, verbose_name='Prev day lowest price', max_digits=20, decimal_places=5)),
                ('prev_vol', models.IntegerField(default=0, verbose_name='Prev day volume')),
                ('day_open', models.DecimalField(default=0.0, verbose_name='Today opening price', max_digits=20, decimal_places=5)),
                ('pe', models.DecimalField(default=0.0, verbose_name='P/E', max_digits=20, decimal_places=5)),
                ('bid', models.DecimalField(default=0.0, verbose_name='Bid price', max_digits=20, decimal_places=5)),
                ('ask', models.DecimalField(default=0.0, verbose_name='Ask price', max_digits=20, decimal_places=5)),
                ('vol', models.FloatField(default=0.0, verbose_name='Volume (in 000)')),
                ('floating_share', models.FloatField(default=0.0, verbose_name='Floating share(in million)')),
                ('day_high', models.DecimalField(default=0.0, verbose_name='Day high', max_digits=20, decimal_places=5)),
                ('day_low', models.DecimalField(default=0.0, verbose_name='Day low', max_digits=20, decimal_places=5)),
                ('is_in_play', models.BooleanField(default=False, help_text='A stock is in "in play" if it holds an open position.', verbose_name='Does stock have an open position')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyStockDailyIndicator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('indicator', models.CharField(max_length=32, choices=[(b'sma', b'simple moving average'), (b'ema', b'exponential moving average'), (b'wma', b'weighted moving average'), (b'dema', b'double exponential moving average'), (b'tema', b'triple exponential moving average'), (b'trima', b'triangular moving average'), (b'kama', b'Kaufman adaptive moving average'), (b'mama', b'MESA adaptive moving average'), (b't3', b'triple exponential moving average'), (b'macd', b'moving average convergence / divergence'), (b'macdext', b'moving average convergence / divergence values with controllable moving average type'), (b'stoch', b'stochastic oscillator'), (b'stochf', b'stochastic fast'), (b'rsi', b'relative strength index'), (b'stochrsi', b'stochastic relative strength index'), (b'willr', b"Williams' %R"), (b'adx', b'average directional movement index'), (b'adxr', b'average directional movement index rating'), (b'apo', b'absolute price oscillator'), (b'ppo', b'percentage price oscillator'), (b'mom', b'momentum'), (b'bop', b'balance of power'), (b'cci', b'commodity channel index'), (b'cmo', b'Chande momentum oscillator'), (b'roc', b'rate of change'), (b'rocr', b'rate of change ratio'), (b'aroon', b'Aroon'), (b'aroonosc', b'Aroon oscillator'), (b'mfi', b'money flow index'), (b'trix', b'1-day rate of change of a triple smooth exponential moving average'), (b'ultosc', b'ultimate oscillator'), (b'dx', b'directional movement index'), (b'minus_di', b'minus directional indicator'), (b'plus_di', b'plus directional indicator'), (b'minus_dm', b'minus directional movement'), (b'plus_dm', b'plus directional movement'), (b'bbands', b'Bollinger bands'), (b'midpoint', b'MIDPOINT = (highest value + lowest value)/2'), (b'midprice', b'MIDPRICE = (highest high + lowest low)/2'), (b'sar', b'parabolic SAR'), (b'trange', b'true range'), (b'atr', b'average true range'), (b'natr', b'normalized average true range'), (b'ad', b'Chaikin A/D line'), (b'adosc', b'Chaikin A/D oscillator'), (b'obv', b'balance volume'), (b'ht_trendline', b'Hilbert transform, instantaneous trendline'), (b'ht_sine', b'Hilbert transform, sine wave'), (b'ht_trendmode', b'Hilbert transform, trend vs cycle mode'), (b'ht_dcperiod', b'Hilbert transform, dominant cycle period'), (b'ht_dcphase', b'Hilbert transform, dominant cycle phase'), (b'ht_phasor', b'Hilbert transform, phasor components')])),
                ('date_stamp', models.DateField(verbose_name='Date')),
                ('interval', models.IntegerField(default=1, choices=[(1, b'daily'), (2, b'weekly'), (3, b'monthly')])),
                ('time_period', models.IntegerField(default=2, help_text='Number of data points used to calculate each moving average value. Positive integers are accepted.')),
                ('series_type', models.CharField(max_length=8, choices=[(b'o', b'open price'), (b'c', b'close price'), (b'l', b'low price'), (b'h', b'high price')])),
                ('fast_period', models.IntegerField(default=12)),
                ('slow_period', models.IntegerField(default=26)),
                ('ma_type', models.IntegerField(default=0)),
                ('fast_limit', models.FloatField(default=0.01)),
                ('slow_limit', models.FloatField(default=0.01)),
                ('signal_period', models.IntegerField(default=9)),
                ('fast_ma_type', models.IntegerField(default=0)),
                ('slow_ma_type', models.IntegerField(default=0)),
                ('signal_ma_type', models.IntegerField(default=0)),
                ('fast_kperiod', models.IntegerField(default=5)),
                ('slow_kperiod', models.IntegerField(default=3)),
                ('slow_dperiod', models.IntegerField(default=3)),
                ('slow_kma_type', models.IntegerField(default=0)),
                ('slow_dma_type', models.IntegerField(default=0)),
                ('fast_dperiod', models.IntegerField(default=3)),
                ('fast_dma_type', models.IntegerField(default=0)),
                ('time_period1', models.IntegerField(default=7)),
                ('time_period2', models.IntegerField(default=14)),
                ('time_period3', models.IntegerField(default=28)),
                ('nbdevup', models.IntegerField(default=2)),
                ('nbdevdn', models.IntegerField(default=2)),
                ('acceleration', models.FloatField(default=0.01)),
                ('max_acceleration', models.FloatField(default=0.2)),
                ('value', models.DecimalField(verbose_name='Indicator value', max_digits=20, decimal_places=3)),
                ('stock', models.ForeignKey(to='stock.MyStock')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyStockHistorical',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('interval', models.IntegerField(default=1, choices=[(1, b'daily'), (2, b'weekly'), (3, b'monthly')])),
                ('date_stamp', models.DateField()),
                ('open_price', models.DecimalField(verbose_name='Open', max_digits=20, decimal_places=3)),
                ('high_price', models.DecimalField(verbose_name='High', max_digits=20, decimal_places=3)),
                ('low_price', models.DecimalField(verbose_name='Low', max_digits=20, decimal_places=3)),
                ('close_price', models.DecimalField(verbose_name='Close', max_digits=20, decimal_places=3)),
                ('vol', models.FloatField(verbose_name='Trading volume (000)')),
                ('adj_open', models.DecimalField(default=-1, verbose_name='Adjusted open', max_digits=20, decimal_places=3)),
                ('adj_high', models.DecimalField(default=-1, verbose_name='Adjusted high', max_digits=20, decimal_places=3)),
                ('adj_low', models.DecimalField(default=-1, verbose_name='Adjusted low', max_digits=20, decimal_places=3)),
                ('adj_close', models.DecimalField(default=-1, verbose_name='Adjusted close', max_digits=20, decimal_places=3)),
                ('adj_factor', models.FloatField(default=0, verbose_name='Adjustment factor')),
                ('amount', models.FloatField(default=-1, verbose_name='Trading amount \u6210\u4ea4\u91d1\u989d (000)')),
                ('status', models.IntegerField(default=-1, verbose_name='Stock trading status, eg. stopped trading on that day')),
                ('stock', models.ForeignKey(to='stock.MyStock')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyTaggedItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tag', models.SlugField(default=b'', max_length=16, verbose_name='Tag')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MyUserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('per_trade_total', models.DecimalField(default=1000.0, verbose_name='Per trade dollar amount', max_digits=20, decimal_places=3)),
                ('pe_threshold', models.CharField(default=b'20-100', max_length=16, verbose_name='P/E threshold')),
                ('cash', models.DecimalField(default=10000, verbose_name='Account balance', max_digits=20, decimal_places=2)),
                ('owner', models.OneToOneField(default=None, to=settings.AUTH_USER_MODEL, help_text=b'', verbose_name='\u7528\u6237')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='mystockhistorical',
            unique_together=set([('stock', 'date_stamp', 'interval')]),
        ),
        migrations.AlterIndexTogether(
            name='mystockhistorical',
            index_together=set([('stock', 'date_stamp', 'interval')]),
        ),
        migrations.AlterUniqueTogether(
            name='mysimulationcondition',
            unique_together=set([('data_source', 'strategy', 'strategy_value', 'data_sort', 'start', 'end', 'capital', 'per_trade', 'buy_cutoff', 'sell_cutoff')]),
        ),
        migrations.AddField(
            model_name='myposition',
            name='simulation',
            field=models.ForeignKey(to='stock.MySimulationCondition'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myposition',
            name='stock',
            field=models.ForeignKey(verbose_name='Stock', to='stock.MyStock'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='myposition',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
