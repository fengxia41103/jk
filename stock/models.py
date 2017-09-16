# -*- coding: utf-8 -*-

import itertools
import logging
from datetime import datetime as dt
from decimal import Decimal
from math import fabs

import numpy as np
from annoying.fields import JSONField  # django-annoying
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Avg
from django.db.models import Count
from django.db.models import F
from django.db.models import Max
from django.db.models import Min
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.forms import ModelForm
from django.utils import timezone
######################################################
#
#   RESTful API endpoints
#
#####################################################
from rest_framework import filters
from rest_framework import serializers
from rest_framework import viewsets

logger = logging.getLogger('jk')
logger.setLevel(logging.DEBUG)

TECH_INDICATORS = (
    ('sma', 'simple moving average'),
    ('ema', 'exponential moving average'),
    ('wma', 'weighted moving average')
)


class MyBaseModel (models.Model):
    # fields
    hash = models.CharField(
        max_length=256,  # we don't expect using a hash more than 256-bit long!
        null=True,
        blank=True,
        default='',
        verbose_name=u'MD5 hash'
    )

    # basic value fields
    name = models.CharField(
        default=None,
        max_length=128,
        verbose_name=u'名称'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=u'描述'
    )

    # help text
    help_text = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name=u'帮助提示'
    )

    # attachments
    attachments = GenericRelation('Attachment')

    # this is an Abstract model
    class Meta:
        abstract = True

    def __unicode__(self):
        return self.name

######################################################
#
#   Tags
#
#####################################################


class MyTaggedItem (models.Model):
    # basic value fields
    tag = models.SlugField(
        default='',
        max_length=16,
        verbose_name=u'Tag'
    )

    def __unicode__(self):
        return self.tag

######################################################
#
#   Attachments
#
#####################################################


class Attachment (models.Model):
    # generic foreign key to base model
    # so we can link attachment to any model defined below
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # instance fields
    created_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        default=None,
        verbose_name=u'创建用户',
        help_text=''
    )

    # basic value fields
    name = models.CharField(
        default='default name',
        max_length=64,
        verbose_name=u'附件名称'
    )
    description = models.CharField(
        max_length=64,
        default='default description',
        verbose_name=u'附件描述'
    )
    file = models.FileField(
        upload_to='%Y/%m/%d',
        verbose_name=u'附件',
        help_text=u'附件'
    )

    def __unicode__(self):
        return self.file.name


class AttachmentForm(ModelForm):

    class Meta:
        model = Attachment
        fields = ['description', 'file']

######################################################
#
#   App specific models
#
#####################################################


class MyStockCustomManager(models.Manager):
    """Custom model manager
    """

    def filter_by_user_pe_threshold(self, user):
        """Filter by PE threshold defined in user profile.

        Args:
                :user: User model object. Each user has a 1-1 relashionship to a UserProfile.
        """
        data = self.get_queryset()

        # get user profile
        user_profile, created = MyUserProfile.objects.get_or_create(owner=user)
        pe_low = int(user_profile.pe_threshold.split('-')[0])
        pe_high = int(user_profile.pe_threshold.split('-')[1])
        return data.filter(pe__gte=pe_low, pe__lte=pe_high)

    def in_heat(self, user):
        """Filter previou day change is > 0.

        Args:
                :user: User model object.
        """
        # data = self.filter_by_user_pe_threshold(user).filter(prev_change__gt=0,day_open__lte=F('prev_close')).order_by('-prev_change')[:top_count]
        data = self.filter_by_user_pe_threshold(user).filter(
            prev_change__gt=0).order_by('-prev_change')
        return data


class MyStock(models.Model):
    # custom managers
    # Note: the 1st one defined will be taken as the default!
    objects = MyStockCustomManager()

    company_name = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=u'Company name'
    )
    symbol = models.CharField(
        max_length=8,
        verbose_name=u'Stock symbol'
    )
    sector = models.CharField(
        max_length=64,
        default='unknown',
        verbose_name=u'Sector name'
    )
    is_sp500 = models.BooleanField(
        default=False,
        verbose_name=u'Is a SP500 stock'
    )
    is_composite = models.BooleanField(
        default=False,
        verbose_name=u'Is a composite stock',
        help_text=u'Composite is a derived value from basket of stocks'
    )

    is_in_play = models.BooleanField(
        default=False,
        verbose_name=u'Does stock have an open position',
        help_text=u'A stock is in "in play" if it holds an open position.'
    )

    def __unicode__(self):
        return '%s (%s)' % (self.symbol, self.company_name)


@receiver(pre_save, sender=MyStock)
def stock_update_handler(sender, **kwargs):
    """MyStock presave hook.
    """
    instance = kwargs.get('instance')
    if instance.id:
        original = MyStock.objects.get(id=instance.id)

        # # spot price changed
        # if original.last != instance.last and instance.day_open:
        #     # update day_change
        #     instance.day_change = (
        #         instance.last - instance.day_open) / instance.day_open * Decimal(100)

        # # if ask or bid changed
        # if original.ask != instance.ask or original.bid != instance.bid:
        #     instance.spread = instance.ask - instance.bid

        # # if vol changed
        # if original.vol != instance.vol and instance.float_share:
        #     instance.vol_over_float = instance.vol / instance.float_share / 10


class MyStockDailyIndicator(models.Model):
    """Model to hold all technical indicators.

    For list: https://www.alphavantage.co/documentation/#technical-indicators
    """
    INDICATOR_CHOICES = TECH_INDICATORS
    his = models.ForeignKey('MyStockHistorical')
    indicator = models.CharField(max_length=32,
                                 choices=INDICATOR_CHOICES)


class MyStockHistorical(models.Model):
    """Model to save historical stock data.
    """
    AGGREGATION_PERIODS = (
        (1, 'daily'),
        (2, 'weekly'),
        (3, 'monthly')
    )
    period = models.IntegerField(
        choices=AGGREGATION_PERIODS,
        default=1)
    stock = models.ForeignKey(
        'MyStock',
        verbose_name=u'Stock'
    )
    date_stamp = models.DateField(
        verbose_name=u'Date'
    )
    open_price = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Open'
    )
    high_price = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        verbose_name=u'High'
    )
    low_price = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Low'
    )
    close_price = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Close'
    )
    vol = models.FloatField(
        verbose_name=u'Trading volume (000)'
    )
    adj_open = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Adjusted open'
    )
    adj_high = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Adjusted high'
    )
    adj_low = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Adjusted low'
    )
    adj_close = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=3,
        verbose_name=u'Adjusted close'
    )
    adj_factor = models.FloatField(
        default=0,
        verbose_name=u'Adjustment factor'
    )
    amount = models.FloatField(
        default=-1,
        verbose_name=u'Trading amount 成交金额 (000)'
    )
    status = models.IntegerField(
        default=-1,
        verbose_name=u'Stock trading status, eg. stopped trading on that day'
    )

    # pre-computed index values
    daily_return = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"(Today's close - Today's Open)/Today's Open*100"
    )

    # due to stock split, we have to use adj close
    # instead of open price, unless we could acquire adjusted open also
    overnight_return = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"(Today's adj close - Yesterday's adj close)/Yesterday's adj close*100"
    )

    def _avg_price(self):
        """Average stock price.

        Avg = total trading amount / total trading volume
        """
        if self.vol and self.amount:
            return Decimal(self.amount) / Decimal(self.vol)
        else:
            return None
    avg_price = property(_avg_price)

    class Meta:
        unique_together = ('stock', 'date_stamp')
        index_together = ['stock', 'date_stamp']


class MyUserProfile(models.Model):
    """User profile model.

    Mode to save user specific configuration values.
    """
    owner = models.OneToOneField(
        User,
        default=None,
        verbose_name=u'用户',
        help_text=''
    )
    per_trade_total = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        default=1000.0,
        verbose_name=u'Per trade dollar amount'
    )
    pe_threshold = models.CharField(
        max_length=16,
        default='20-100',
        verbose_name=u'P/E threshold'
    )
    cash = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=10000,
        verbose_name=u'Account balance'
    )

    def _equity(self):
        """User equity position.

        User equity position is the aggregation
        of all his open portfolio.
        """
        pos = [p.total for p in MyPosition.objects.filter(
            user=self.owner, is_open=True)]
        return sum(pos)
    equity = property(_equity)

    def _asset(self):
        """User asset.

        Asset = cash + equity
        """
        return self.cash + self.equity
    asset = property(_asset)


class MyPosition(models.Model):
    """Stock position on portfolio.

    Each position is a stock that user is currently holding.
    A position is like a tiny accounting book:
        :position: cost we paid when buying these stocks
        :vol: qty
        :close_position: price we took when selling these stocks

    The difference between the buy and sell will be the gain/loss
    we took buy doing this trade. Also, as long as we are holding it,
    its value fluctuates along with the market. Thus the source
    of final gain/loss came from two places:
        1. diff between cost and exit price
        2. fluctuation from the market
    """
    created = models.DateTimeField(
        auto_now_add=True,
    )
    user = models.ForeignKey(User)
    simulation = models.ForeignKey(
        'MySimulationCondition'
    )
    stock = models.ForeignKey(
        'MyStock',
        verbose_name=u'Stock'
    )
    position = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        verbose_name=u'We paid'
    )
    vol = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        default=0,
        verbose_name=u'Trade vol'
    )
    is_open = models.BooleanField(
        default=True,
        verbose_name=u'Is position open'
    )
    last_updated_on = models.DateTimeField(
        auto_now=True
    )
    close_position = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        default=0.0,
        verbose_name=u'We closed at'
    )
    open_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=u'Position open date'
    )
    close_date = models.DateField(
        null=True,
        blank=True,
        default=None,  # if close_date == None, this is an open position
        verbose_name=u'Position close date'
    )
    life_in_days = models.IntegerField(
        default=0,
        verbose_name=u'Life in days'
    )
    gain = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        default=0.0,
        verbose_name=u'Gain'
    )
    cost = models.DecimalField(
        max_digits=20,
        decimal_places=3,
        default=0.0,
        verbose_name=u'Cost'
    )

    def add(self, user, price, vol, source='simulation', on_date=None):
        """
        Utility function to buy or sell.

        If vol > 0: buy; < 0: sell.
        If updated vol == 0, this position will be marked "closed".

        User profile's cash will be updated:
        if buy: cash -= price * vol
        if sell: cash += price * vol

        Args:
                :user: User object. This is also the owner of this position. Buying request
                will be compared against user's quota.
                :price: buying at price
                :vol: buying vol
                :source: used to track live trading. Not used.
                :on_date: trading date. Not used.
        """

        # new position = weighted avg
        self.position = (self.position * self.vol +
                         price * vol) / (self.vol + vol)
        self.vol += vol
        if not self.vol:
            self.is_open = False
        if on_date:
            self.open_date = on_date
        else:
            self.open_date = dt.now().date()

        """Cost to establish this position.

        cost = position price * holding volume
        """
        self.cost = self.position * self.vol
        self.save()

    def close(self, user, price, on_date=None):
        """Close position.

        Closed price at requested price.

        Args:
                :price: selling price.
        """
        self.close_position = price
        self.is_open = False
        if on_date:
            self.close_date = on_date
        else:
            self.close_date = dt.now().date()
        self.life_in_days = (self.close_date - self.open_date).days

        """Realized gain/loss.

        Profit/loss realized by holding this stock till closing.
        """
        self.gain = (self.close_position - self.position) * self.vol
        self.save()

    def _potential_gain(self):
        """Unrealized gain/loss.

        Unrealized gain/loss is estimated by comparing
        the last spot price over our initial position price.
        """
        return (self.stock.last - self.position) * self.vol
    potential_gain = property(_potential_gain)

    def _to_last_pcnt(self):
        """Unrealized gain/loss in pcnt.
        """
        return (self.stock.last - self.position) / self.position * 100.0
    to_last_pcnt = property(_to_last_pcnt)

    def _total(self):
        """Spot value.

        Current position value based on the last spot price.
        """
        return self.stock.last * self.vol
    total = property(_total)

    def _elapse_in_days(self):
        """Stock's life in days as of now.
        """
        return (dt.now().date() - self.created.date()).days
    elapse_in_days = property(_elapse_in_days)


@receiver(pre_save, sender=MyPosition)
def day_change_handler(sender, **kwargs):
    instance = kwargs.get('instance')
    if instance.close_date:
        instance.is_open = False
    if instance.is_open:
        stock = MyStock.objects.get(id=instance.stock.id)
        if not stock.is_in_play:
            stock.is_in_play = True
            stock.save()


class MySimulationCondition(models.Model):
    """Simulation condition model.

    A simulation condition represents a particular
    set of parameters that form the context of a simulation run,
    eg. which data set to use, what date period to use,
    how many capital to begin with, and how much
    we want to spend per trade.

    Fields:
            :strategy: Defines which strategy one would
                    use for a simulation run.
                    S1 strategy calls for an index value precalculated based on
                    certain algorithm and trade based; S2 is a buy low sell high strategy
                    that will monitor a stock's open/close/spot to determine when to buy
                    and when to sell.
            :buy_cutoff: If a stock has dropped over buy_cutoff percentage,
                    one buys this stock. This value has different meanings in 
                    different strategies. In S1, this is the cutoff band
                    that has grouped stocked based on a pre-computed index value;
                    in S2, this is daily drop %.
            :sell_cutoff: As the counterpart to the buy_cutoff, sell_cutoff
                    defines a percentage that one would close a position.
                    In S1 this is the band when a stock falls outof a artificial band
                    determined by a pre-computed index value; in S2 this is the 
                    percentage relative to the initial price at buying.
    """
    DATA_CHOICES = (
        (1, "S&P500"),
    )
    DATA_SORT_CHOICES = (
        (0, "ascending"),
        (1, "descending"),
    )
    STRATEGY_CHOICES = (
        (1, "S1 (by ranking)"),
        (2, "S2 (buy low sell high)"),
    )
    INDICATOR_CHOICES = TECH_INDICATORS
    data_source = models.IntegerField(
        choices=DATA_CHOICES,
        default=1
    )
    strategy = models.IntegerField(
        choices=STRATEGY_CHOICES,
        default=1
    )
    strategy_value = models.IntegerField(
        choices=INDICATOR_CHOICES,
        default=1,
        verbose_name=u"Strategy value"
    )
    data_sort = models.IntegerField(
        choices=DATA_SORT_CHOICES,
        default=2,
        verbose_name=u"Sort order"
    )
    start = models.DateField(
        default="2014-01-01",
        verbose_name=u'Start date'
    )
    end = models.DateField(
        default="2014-01-10",
        verbose_name=u'End date',
    )
    capital = models.IntegerField(
        default=100000,
        verbose_name=u"Starting cash"
    )
    per_trade = models.IntegerField(
        default=10000,
        verbose_name=u"Per trade amount"
    )
    buy_cutoff = models.IntegerField(
        default=25,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ],
        verbose_name="Buy cutoff (%)"
    )
    sell_cutoff = models.IntegerField(
        default=75,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ],
        verbose_name="Sell cutoff (%)"
    )

    def __unicode__(self):
        if self.sector:
            return u'%s-%s-%s (%d-%d), %s - %s' % (self.sector.code,
                                                   self.get_strategy_display(),
                                                   self.get_strategy_value_display(),
                                                   self.buy_cutoff,
                                                   self.sell_cutoff,
                                                   self.start,
                                                   self.end)
        else:
            return '%s-%s-%s (%d-%d), %s - %s' % (self.get_data_source_display(),
                                                  self.get_strategy_display(),
                                                  self.get_strategy_value_display(),
                                                  self.buy_cutoff,
                                                  self.sell_cutoff,
                                                  self.start,
                                                  self.end)

    class Meta:
        unique_together = ("data_source",
                           "strategy",
                           "strategy_value",
                           "data_sort",
                           "start",
                           "end",
                           "capital",
                           "per_trade",
                           "buy_cutoff",
                           "sell_cutoff")

    def _snapshots(self):
        return MySimulationSnapshot.objects.filter(simulation=self)
    snapshots = property(_snapshots)

    def _snapshots_sort_by_date(self):
        return MySimulationSnapshot.objects.filter(simulation=self).order_by('on_date')
    snapshots_sort_by_date = property(_snapshots_sort_by_date)

    def _assets(self):
        return MySimulationSnapshot.objects.filter(simulation=self).values_list('asset', flat=True).order_by('on_date')
    assets = property(_assets)

    def _equities(self):
        return MySimulationSnapshot.objects.filter(simulation=self).values_list('equity', flat=True).order_by('on_date')
    equities = property(_equities)

    def _cashes(self):
        return MySimulationSnapshot.objects.filter(simulation=self).values_list('cash', flat=True).order_by('on_date')
    cashes = property(_cashes)

    def _num_of_buys(self):
        """Total number of buys.

        This is computed from individual buys.
        """
        return MyPosition.objects.filter(simulation=self).count()
    num_of_buys = property(_num_of_buys)

    def _num_of_sells(self):
        """Total number of sells.

        This is computed from individual sells.
        """
        return MyPosition.objects.filter(simulation=self, is_open=False).count()
    num_of_sells = property(_num_of_sells)

    def _asset_daily_return(self):
        """User asset's daily change in pcnt.

        This index shows how a user's asset fluctuates from day to day
        during simulation period.
        """
        return MySimulationSnapshot.objects.filter(simulation=self).values_list('asset_gain_pcnt', flat=True).order_by('on_date')
    asset_daily_return = property(_asset_daily_return)

    def _asset_gain_pcnt_t0(self):
        """Measures daily asset's return over T0's.

        This index shows how assets swings comparing to simulation's T0.
        This can be viewed as an overall performance indicator over time.
        """
        # return [x.asset_gain_pcnt_t0 for x in self.snapshots]
        return list(MySimulationSnapshot.objects.filter(simulation=self).values_list('asset_gain_pcnt_t0', flat=True).order_by('on_date'))
    asset_gain_pcnt_t0 = property(_asset_gain_pcnt_t0)

    def _asset_end_return(self):
        """Last's day's cumulative return.
        """
        if self.asset_gain_pcnt_t0:
            return self.asset_gain_pcnt_t0[-1]
        return None
    asset_end_return = property(_asset_end_return)

    def _asset_max_return(self):
        """Best return % during simulation period.

        This indicator shows the maximum potential gain from
        applied strategy.
        """
        return max(self.asset_gain_pcnt_t0)
    asset_max_return = property(_asset_max_return)

    def _asset_min_return(self):
        """Worst return rate during simulation period.

        This shows the worst moment this strategy can yield.
        """
        return min(self.asset_gain_pcnt_t0)
    asset_min_return = property(_asset_min_return)

    def _asset_cumulative_return_mean(self):
        """Average gain.

        Numeric mean of gains. This indicates the likely gain one can achieve 
        by applying this strategy.  
        """
        return np.mean(self.asset_gain_pcnt_t0)
    asset_cumulative_return_mean = property(_asset_cumulative_return_mean)

    def _asset_cumulative_return_std(self):
        """Standard deviation of cumulative gains.

        This measures the risk of applied strategy using cumulative gain data.
        """
        return np.std(self.asset_gain_pcnt_t0)
    asset_cumulative_return_std = property(_asset_cumulative_return_std)

    def _gain_from_holding(self):
        """Equity gains from holding.

        This tracks equity gains from holding a particular stock,
        not from trading it. It indicates
        how well equities were performing. This is completely determined by
        how well we picked stock, thus is a good indicator of applied strategy.
        """
        return MySimulationSnapshot.objects.filter(simulation=self).values_list('gain_from_holding', flat=True).order_by('on_date')
    gain_from_holding = property(_gain_from_holding)

    def _gain_from_exit(self):
        return MySimulationSnapshot.objects.filter(simulation=self).values_list('gain_from_exit', flat=True).order_by('on_date')
    gain_from_exit = property(_gain_from_exit)

    def _equity_life_in_days(self):
        """Equity life in days.

        We want to measure how long we usually hold a position. By monitoing
        this value, we could apply a strategy that dictate 
        by how long we can hold a position.
        """
        life_in_days = MyPosition.objects.filter(simulation=self, is_open=False).annotate(
            max_life=Max('life_in_days'),
            avg_life=Avg('life_in_days')
        )

        # life_in_days = [s.life_in_days for s in sells]

        # index [0] is the min(), [-1] is the max()floatformat
        # min is skipped since it is always 0 because
        # we may be buying and unloading a stock on the same day
        return (('max', life_in_days['max_life']), ('Avg', life_in_days['avg_life']))
    equity_life_in_days = property(_equity_life_in_days)

    def _stock_sell_stat(self):
        """Stats of individual stock selling history.
        """
        sells = MyPosition.objects.annotate(
            max_life=Max('life_in_days'),
            min_life=Min('life_in_days'),
            avg_life=Avg('life_in_days'),
            num_of_trades=Count('symbol')
        ).filter(simulation=self, is_open=False)
        return sells
    stock_sell_stat = property(_stock_sell_stat)


class MySimulationSnapshot(models.Model):
    """Simulation snapshot.
    """
    # custom managers
    # Note: the 1st one defined will be taken as the default!
    # objects = MyStockCustomManager()

    simulation = models.ForeignKey('MySimulationCondition')
    on_date = models.DateField(
        default="2014-01-01",
        verbose_name=u'Snapshot date'
    )
    cash = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        verbose_name=u'Cash',
        default=0
    )
    equity = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        verbose_name=u'Equity',
        default=0
    )
    asset = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        verbose_name=u'Asset',
        default=0
    )
    gain_from_holding = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        verbose_name=u'Gain from holding',
        default=0
    )
    gain_from_exit = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        verbose_name=u'Gain from exit',
        default=0
    )
    asset_gain_pcnt = models.FloatField(
        verbose_name=u'Asset gain from previous day',
        default=0,
        help_text=u"This measures asset return in pcnt comparing to previous day"
    )
    asset_gain_pcnt_t0 = models.FloatField(
        verbose_name=u'Asset gain from T0',
        default=0,
        help_text=u"This measures asset return in pcnt comparing to T0's"
    )

    def _buy_transactions(self):
        """Buy transactions.

        A buy transaction will create a MyPosition, which
        has a MyCondition and on_date. Using these values
        are sufficient to determine that this position was created
        by our simulation run and belongs to this snapshot (by on_date).
        """
        buys = MyPosition.objects.filter(
            simulation=self.simulation,
            open_date=self.on_date  # this is when position was created as a buy
        ).order_by('stock__symbol')
        return buys
    buy_transactions = property(_buy_transactions)

    def _sell_transactions(self):
        """Sell transactions.

        The difference from a buy transaction is to filter MyPosition by close_date
        instead of open_date.
        """
        sells = MyPosition.objects.filter(
            simulation=self.simulation,
            close_date=self.on_date  # this is when position was closed as a sell
        ).order_by('stock__symbol')
        return sells
    sell_transactions = property(_sell_transactions)

    def _equities(self):
        """Stocks on my portfolio.

        MyPosition is on portfilio if:
        1. its open date is less than on_date;
        2. its close date is either missing (still opened) or later than on_date
        """
        return MyPosition.objects.filter(
            Q(simulation=self.simulation) & Q(open_date__lte=self.on_date),
            Q(close_date__isnull=True) | Q(close_date__gt=self.on_date)
        ).order_by('stock__symbol')

    equities = property(_equities)


# Serializers define the API representation.


class MyStockSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = MyStock

# ViewSets define the view behavior.


class MyStockViewSet(viewsets.ModelViewSet):
    queryset = MyStock.objects.all()
    serializer_class = MyStockSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('symbol', )
