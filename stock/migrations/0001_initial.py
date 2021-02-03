# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import django.core.validators
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "name",
                    models.CharField(
                        default=b"default name",
                        max_length=64,
                        verbose_name="\u9644\u4ef6\u540d\u79f0",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        default=b"default description",
                        max_length=64,
                        verbose_name="\u9644\u4ef6\u63cf\u8ff0",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        help_text="\u9644\u4ef6",
                        upload_to=b"%Y/%m/%d",
                        verbose_name="\u9644\u4ef6",
                    ),
                ),
                ("content_type", models.ForeignKey(to="contenttypes.ContentType")),
                (
                    "created_by",
                    models.ForeignKey(
                        default=None,
                        to=settings.AUTH_USER_MODEL,
                        blank=True,
                        help_text=b"",
                        null=True,
                        verbose_name="\u521b\u5efa\u7528\u6237",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MyPosition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True)),
                (
                    "position",
                    models.DecimalField(
                        verbose_name="We paid", max_digits=20, decimal_places=4
                    ),
                ),
                (
                    "vol",
                    models.DecimalField(
                        default=0,
                        verbose_name="Trade vol",
                        max_digits=20,
                        decimal_places=4,
                    ),
                ),
                (
                    "is_open",
                    models.BooleanField(default=True, verbose_name="Is position open"),
                ),
                ("last_updated_on", models.DateTimeField(auto_now=True)),
                (
                    "close_position",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="We closed at",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "open_date",
                    models.DateField(
                        null=True, verbose_name="Position open date", blank=True
                    ),
                ),
                (
                    "close_date",
                    models.DateField(
                        default=None,
                        null=True,
                        verbose_name="Position close date",
                        blank=True,
                    ),
                ),
                (
                    "life_in_days",
                    models.IntegerField(default=0, verbose_name="Life in days"),
                ),
                (
                    "gain",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Gain",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "cost",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Cost",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MySector",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("code", models.CharField(max_length=8, verbose_name="Sector code")),
                (
                    "source",
                    models.CharField(max_length=32, verbose_name="Definition source"),
                ),
                ("name", models.CharField(max_length=32, null=True, blank=True)),
                ("description", models.TextField(null=True, blank=True)),
                (
                    "parent",
                    models.ForeignKey(
                        default=None,
                        blank=True,
                        to="stock.MySector",
                        null=True,
                        verbose_name="Parent sector",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MySimulationCondition",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "data_source",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, b"S&P500"),
                            (2, b"CI00*"),
                            (3, b"WIND 8821*"),
                            (4, b"China stock"),
                            (5, b"WIND 2nd-tier sector"),
                        ],
                    ),
                ),
                (
                    "strategy",
                    models.IntegerField(
                        default=1,
                        choices=[
                            (1, b"S1 (by ranking)"),
                            (2, b"S2 (buy low sell high)"),
                            (3, b"S3 (buy high sell low)"),
                        ],
                    ),
                ),
                (
                    "strategy_value",
                    models.IntegerField(
                        default=1,
                        verbose_name="Strategy value",
                        choices=[
                            (1, b"Daily return"),
                            (2, b"Relative (H,L)"),
                            (3, b"Relative Moving Avg"),
                        ],
                    ),
                ),
                (
                    "data_sort",
                    models.IntegerField(
                        default=2,
                        verbose_name="Sort order",
                        choices=[(0, b"ascending"), (1, b"descending")],
                    ),
                ),
                (
                    "start",
                    models.DateField(default=b"2014-01-01", verbose_name="Start date"),
                ),
                (
                    "end",
                    models.DateField(default=b"2014-01-10", verbose_name="End date"),
                ),
                (
                    "capital",
                    models.IntegerField(default=100000, verbose_name="Starting cash"),
                ),
                (
                    "per_trade",
                    models.IntegerField(default=10000, verbose_name="Per trade amount"),
                ),
                (
                    "buy_cutoff",
                    models.IntegerField(
                        default=25,
                        verbose_name=b"Buy cutoff (%)",
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                    ),
                ),
                (
                    "sell_cutoff",
                    models.IntegerField(
                        default=75,
                        verbose_name=b"Sell cutoff (%)",
                        validators=[
                            django.core.validators.MaxValueValidator(100),
                            django.core.validators.MinValueValidator(0),
                        ],
                    ),
                ),
                (
                    "sector",
                    models.ForeignKey(
                        default=None,
                        blank=True,
                        to="stock.MySector",
                        null=True,
                        verbose_name="Data source sector",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MySimulationSnapshot",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "on_date",
                    models.DateField(
                        default=b"2014-01-01", verbose_name="Snapshot date"
                    ),
                ),
                (
                    "cash",
                    models.DecimalField(
                        default=0, verbose_name="Cash", max_digits=20, decimal_places=4
                    ),
                ),
                (
                    "equity",
                    models.DecimalField(
                        default=0,
                        verbose_name="Equity",
                        max_digits=20,
                        decimal_places=4,
                    ),
                ),
                (
                    "asset",
                    models.DecimalField(
                        default=0, verbose_name="Asset", max_digits=20, decimal_places=4
                    ),
                ),
                (
                    "gain_from_holding",
                    models.DecimalField(
                        default=0,
                        verbose_name="Gain from holding",
                        max_digits=20,
                        decimal_places=4,
                    ),
                ),
                (
                    "gain_from_exit",
                    models.DecimalField(
                        default=0,
                        verbose_name="Gain from exit",
                        max_digits=20,
                        decimal_places=4,
                    ),
                ),
                (
                    "asset_gain_pcnt",
                    models.FloatField(
                        default=0,
                        help_text="This measures asset return in pcnt comparing to previous day",
                        verbose_name="Asset gain from previous day",
                    ),
                ),
                (
                    "asset_gain_pcnt_t0",
                    models.FloatField(
                        default=0,
                        help_text="This measures asset return in pcnt comparing to T0's",
                        verbose_name="Asset gain from T0",
                    ),
                ),
                ("simulation", models.ForeignKey(to="stock.MySimulationCondition")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MyStock",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "company_name",
                    models.CharField(
                        max_length=128,
                        null=True,
                        verbose_name="Company name",
                        blank=True,
                    ),
                ),
                ("symbol", models.CharField(max_length=8, verbose_name="Stock symbol")),
                (
                    "sector",
                    models.CharField(
                        default=b"unknown", max_length=64, verbose_name="Sector name"
                    ),
                ),
                (
                    "is_sp500",
                    models.BooleanField(default=False, verbose_name="Is a SP500 stock"),
                ),
                (
                    "is_china_stock",
                    models.BooleanField(default=False, verbose_name="Is a China stock"),
                ),
                (
                    "is_index",
                    models.BooleanField(
                        default=False,
                        help_text="Index is a derived value from basket of stocks",
                        verbose_name="Is an index",
                    ),
                ),
                (
                    "prev_close",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Prev day closing price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "prev_open",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Prev day opening price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "prev_high",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Prev day highest price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "prev_low",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Prev day lowest price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "prev_vol",
                    models.IntegerField(default=0, verbose_name="Prev day volume"),
                ),
                (
                    "day_open",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Today opening price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "pe",
                    models.DecimalField(
                        default=0.0, verbose_name="P/E", max_digits=20, decimal_places=5
                    ),
                ),
                (
                    "bid",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Bid price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "ask",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Ask price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                ("vol", models.FloatField(default=0.0, verbose_name="Volume (in 000)")),
                (
                    "floating_share",
                    models.FloatField(
                        default=0.0, verbose_name="Floating share(in million)"
                    ),
                ),
                (
                    "day_high",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Day high",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "day_low",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Day low",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "last",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Spot price",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "last_update_time",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Spot sample time", null=True
                    ),
                ),
                (
                    "is_in_play",
                    models.BooleanField(
                        default=False, verbose_name="Has pending position"
                    ),
                ),
                (
                    "prev_change",
                    models.FloatField(default=0.0, verbose_name="Prev day change (%)"),
                ),
                (
                    "day_change",
                    models.FloatField(default=0.0, verbose_name="Today change(%)"),
                ),
                (
                    "spread",
                    models.DecimalField(
                        default=0.0,
                        verbose_name="Bid-ask spread",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "vol_over_float",
                    models.FloatField(
                        default=0.0, verbose_name="Vol/floating shares (%)"
                    ),
                ),
                (
                    "week_adjusted_close",
                    models.TextField(
                        default=b"", verbose_name="1-week adjusted closing price"
                    ),
                ),
                (
                    "month_adjusted_close",
                    models.TextField(
                        default=b"", verbose_name="1-month adjusted closing price"
                    ),
                ),
                (
                    "fib_weekly_adjusted_close",
                    models.TextField(
                        default=b"",
                        verbose_name="Fibonacci timezone adjusted closing price",
                    ),
                ),
                (
                    "fib_daily_adjusted_close",
                    models.TextField(
                        default=b"",
                        verbose_name="Fibonacci timezone adjusted closing price",
                    ),
                ),
                (
                    "fib_weekly_score",
                    models.FloatField(
                        default=0, verbose_name="Weighed sum of weekly adj close price"
                    ),
                ),
                (
                    "fib_daily_score",
                    models.FloatField(
                        default=0, verbose_name="Weighed sum of daily adj close price"
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MyStockHistorical",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                ("date_stamp", models.DateField(verbose_name="Date")),
                (
                    "open_price",
                    models.DecimalField(
                        verbose_name="Open", max_digits=20, decimal_places=5
                    ),
                ),
                (
                    "high_price",
                    models.DecimalField(
                        verbose_name="High", max_digits=20, decimal_places=5
                    ),
                ),
                (
                    "low_price",
                    models.DecimalField(
                        verbose_name="Low", max_digits=20, decimal_places=5
                    ),
                ),
                (
                    "close_price",
                    models.DecimalField(
                        verbose_name="Close", max_digits=20, decimal_places=5
                    ),
                ),
                (
                    "adj_open",
                    models.DecimalField(
                        default=-1,
                        verbose_name="Adjusted open",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "adj_high",
                    models.DecimalField(
                        default=-1,
                        verbose_name="Adjusted high",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "adj_low",
                    models.DecimalField(
                        default=-1,
                        verbose_name="Adjusted low",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "adj_close",
                    models.DecimalField(
                        default=-1,
                        verbose_name="Adjusted close",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "adj_factor",
                    models.FloatField(default=0, verbose_name="Adjustment factor"),
                ),
                (
                    "amount",
                    models.FloatField(
                        default=-1, verbose_name="\u6210\u4ea4\u91d1\u989d (000)"
                    ),
                ),
                ("vol", models.FloatField(verbose_name="Volume (000)")),
                (
                    "flag_by_strategy",
                    models.CharField(
                        default=b"U",
                        max_length=1,
                        null=True,
                        verbose_name="Back testing flag",
                        blank=True,
                    ),
                ),
                (
                    "val_by_strategy",
                    models.FloatField(
                        default=0.0,
                        null=True,
                        verbose_name="Computed value based on a strategy",
                        blank=True,
                    ),
                ),
                (
                    "peer_rank",
                    models.IntegerField(
                        default=0,
                        null=True,
                        verbose_name="Ranking among peers",
                        blank=True,
                    ),
                ),
                (
                    "status",
                    models.IntegerField(
                        default=-1,
                        verbose_name="Stock trading status, eg. stopped trading on that day",
                    ),
                ),
                (
                    "daily_return",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="(Today's close - Today's Open)/Today's Open*100",
                        blank=True,
                    ),
                ),
                (
                    "overnight_return",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="(Today's adj close - Yesterday's adj close)/Yesterday's adj close*100",
                        blank=True,
                    ),
                ),
                (
                    "relative_hl",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="Relative Position (H,L)",
                        blank=True,
                    ),
                ),
                (
                    "relative_ma",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="Relative Position Moving Average",
                        blank=True,
                    ),
                ),
                (
                    "lg_slope",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="Linear regression slope",
                        blank=True,
                    ),
                ),
                (
                    "si",
                    models.FloatField(
                        default=None, null=True, verbose_name="SI indicator", blank=True
                    ),
                ),
                (
                    "cci",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="CCI indicator",
                        blank=True,
                    ),
                ),
                (
                    "decycler_oscillator",
                    models.FloatField(
                        default=None,
                        null=True,
                        verbose_name="Decycler oscillator",
                        blank=True,
                    ),
                ),
                ("stock", models.ForeignKey(verbose_name="Stock", to="stock.MyStock")),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MyTaggedItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "tag",
                    models.SlugField(default=b"", max_length=16, verbose_name="Tag"),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="MyUserProfile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "per_trade_total",
                    models.DecimalField(
                        default=1000.0,
                        verbose_name="Per trade dollar amount",
                        max_digits=20,
                        decimal_places=5,
                    ),
                ),
                (
                    "pe_threshold",
                    models.CharField(
                        default=b"20-100", max_length=16, verbose_name="P/E threshold"
                    ),
                ),
                (
                    "cash",
                    models.DecimalField(
                        default=10000,
                        verbose_name="Account balance",
                        max_digits=20,
                        decimal_places=2,
                    ),
                ),
                (
                    "owner",
                    models.OneToOneField(
                        default=None,
                        to=settings.AUTH_USER_MODEL,
                        help_text=b"",
                        verbose_name="\u7528\u6237",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name="mystockhistorical", unique_together=set([("stock", "date_stamp")])
        ),
        migrations.AlterIndexTogether(
            name="mystockhistorical", index_together=set([("stock", "date_stamp")])
        ),
        migrations.AlterUniqueTogether(
            name="mysimulationcondition",
            unique_together=set(
                [
                    (
                        "data_source",
                        "sector",
                        "strategy",
                        "strategy_value",
                        "data_sort",
                        "start",
                        "end",
                        "capital",
                        "per_trade",
                        "buy_cutoff",
                        "sell_cutoff",
                    )
                ]
            ),
        ),
        migrations.AddField(
            model_name="mysector",
            name="stocks",
            field=models.ManyToManyField(to="stock.MyStock"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="myposition",
            name="simulation",
            field=models.ForeignKey(to="stock.MySimulationCondition"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="myposition",
            name="stock",
            field=models.ForeignKey(verbose_name="Stock", to="stock.MyStock"),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="myposition",
            name="user",
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
