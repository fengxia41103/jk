# -*- coding: utf-8 -*-

from django.db import models
from django.contrib import admin
from django.forms import ModelForm
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.generic import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from annoying.fields import JSONField  # django-annoying
from django.db.models import Q, F
from datetime import datetime as dt
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from math import fabs
import numpy as np


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
#	Tags
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
#	Attachments
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
#	App specific models
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


class MySector(models.Model):
    """Sector that is used to group stocks.

    The company that a stock represents is usually
    linked to a sector. Each country may have a different way to
    define these.
    """
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        default=None,
        verbose_name=u'Parent sector'
    )
    code = models.CharField(
        max_length=8,
        verbose_name=u'Sector code'
    )
    source = models.CharField(
        max_length=32,
        verbose_name=u'Definition source'
    )
    name = models.CharField(
        max_length=32,
        null=True,
        blank=True
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    stocks = models.ManyToManyField('MyStock')

    def __unicode__(self):
        if self.name:
            return u'{0} ({1})'.format(self.name, self.code)
        else:
            return self.code


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
    is_china_stock = models.BooleanField(
        default=False,
        verbose_name=u'Is a China stock'
    )
    prev_close = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Prev day closing price'
    )
    prev_open = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Prev day opening price'
    )
    prev_high = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Prev day highest price'
    )
    prev_low = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Prev day lowest price'
    )
    prev_vol = models.IntegerField(
        default=0,
        verbose_name=u'Prev day volume'
    )
    day_open = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Today opening price'
    )
    pe = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'P/E'
    )
    bid = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Bid price'
    )
    ask = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Ask price'
    )
    vol = models.FloatField(
        default=0.0,
        verbose_name=u'Volume (in 000)'
    )
    floating_share = models.FloatField(
        default=0.0,
        verbose_name=u'Floating share(in million)'
    )
    day_high = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Day high'
    )
    day_low = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Day low'
    )

    last = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Spot price'
    )
    last_update_time = models.DateTimeField(
        null=True,
        blank=True,
        auto_now=True,
        verbose_name=u'Spot sample time'
    )
    is_in_play = models.BooleanField(
        default=False,
        verbose_name=u'Has pending position'
    )
    prev_change = models.FloatField(
        default=0.0,
        verbose_name=u'Prev day change (%)'
    )
    day_change = models.FloatField(
        default=0.0,
        verbose_name=u'Today change(%)'
    )
    spread = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        default=0.0,
        verbose_name=u'Bid-ask spread'
    )
    vol_over_float = models.FloatField(
        default=0.0,
        verbose_name=u'Vol/floating shares (%)'
    )
    week_adjusted_close = models.TextField(
        default='',
        verbose_name=u'1-week adjusted closing price'
    )
    month_adjusted_close = models.TextField(
        default='',
        verbose_name=u'1-month adjusted closing price'
    )
    fib_weekly_adjusted_close = models.TextField(
        default='',
        verbose_name=u'Fibonacci timezone adjusted closing price'
    )
    fib_daily_adjusted_close = models.TextField(
        default='',
        verbose_name=u'Fibonacci timezone adjusted closing price'
    )
    fib_weekly_score = models.FloatField(
        default=0,
        verbose_name=u'Weighed sum of weekly adj close price'
    )
    fib_daily_score = models.FloatField(
        default=0,
        verbose_name=u'Weighed sum of daily adj close price'
    )

    def _oneday_change(self):
        """Midday change percentage

        Midday change is computed as:
                (last polled bid price/today's openning price) in %
        """
        if self.day_open:
            return (self.last - self.day_open) / self.day_open * Decimal(100)
        else:
            return None
    oneday_change = property(_oneday_change)

    def _twoday_change(self):
        """Current bid over yesterday's openning price in percentage.
        """
        if self.prev_open:
            return (self.last - self.prev_open) / self.prev_open * Decimal(100)
        else:
            return None
    twoday_change = property(_twoday_change)

    def _week_change(self):
        """Weekly closing price over the same week's openning price.

        Data is saved in week_adjusted_close as (open,close) delimited by comma.
        This format is copied by Yahoo!Finance.
        """
        if self.week_adjusted_close:
            vals = self.week_adjusted_close.split(',')
            return (Decimal(vals[-1]) - Decimal(vals[0])) / Decimal(vals[0]) * Decimal(100)
        else:
            return None
    week_change = property(_week_change)

    def _month_change(self):
        """Closing price over the openning price 1-month ago.
        """
        if self.month_adjusted_close:
            vals = self.month_adjusted_close.split(',')
            return (Decimal(vals[-1]) - Decimal(vals[0])) / Decimal(vals[0]) * Decimal(100)
        else:
            return None
    month_change = property(_month_change)

    def _trend_is_consistent_gain(self):
        """Stock is growing consistently.

        A stock is considered gaining consistent when:
        1. it gained today
        2. it gained since yesterday's opening
        3. it gained in this week
        4. it gained in this month

        Taking four segments forces a stronger check against its price trend.
        There isn't a particular theory behind such check. But IMHO,
        a consistend gain is an indicator of a rare gaining period.
        """
        if self.oneday_change > 0 and self.twoday_change > 0 and self.week_change > 0 and self.month_change > 0:
            return True
        else:
            return False
    trend_is_consistent_gain = property(_trend_is_consistent_gain)

    def _trend_is_consistent_loss(self):
        """Reverse of consistent_gain. See above.
        """
        if self.oneday_change < 0 and self.twoday_change < 0 and self.week_change < 0 and self.month_change < 0:
            return True
        else:
            return False
    trend_is_consistent_loss = property(_trend_is_consistent_loss)

    def _fib_weekly_score_pcnt(self):
        """Fibonacci weekly score in %.

        Score is calculated by sampling in time based on Fib values as time intervals.
        The score is computed offline so it is historically correct.
        """
        if self.last:
            return self.fib_weekly_score / float(self.last) * 100
        else:
            return None
    fib_weekly_score_pcnt = property(_fib_weekly_score_pcnt)

    def _fib_daily_score_pcnt(self):
        """Fibonacci daily score.
        """
        if self.last:
            return self.fib_daily_score / float(self.last) * 100
        else:
            return None
    fib_daily_score_pcnt = property(_fib_daily_score_pcnt)

    def __unicode__(self):
        return '%s (%s)' % (self.symbol, self.company_name)


@receiver(pre_save, sender=MyStock)
def stock_update_handler(sender, **kwargs):
    """MyStock presave hook.
    """
    instance = kwargs.get('instance')
    if instance.id:
        original = MyStock.objects.get(id=instance.id)

        # spot price changed
        if original.last != instance.last and instance.day_open:
            # update day_change
            instance.day_change = (
                instance.last - instance.day_open) / instance.day_open * Decimal(100)

        # if ask or bid changed
        if original.ask != instance.ask or original.bid != instance.bid:
            instance.spread = instance.ask - instance.bid

        # if vol changed
        if original.vol != instance.vol and instance.float_share:
            instance.vol_over_float = instance.vol / instance.float_share / 10


class MyStockHistorical(models.Model):
    """Model to save historical stock data.
    """
    stock = models.ForeignKey(
        'MyStock',
        verbose_name=u'Stock'
    )
    date_stamp = models.DateField(
        verbose_name=u'Date'
    )
    open_price = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Open'
    )
    high_price = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        verbose_name=u'High'
    )
    low_price = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Low'
    )
    close_price = models.DecimalField(
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Close'
    )
    adj_open = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Adjusted open'
    )
    adj_high = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Adjusted high'
    )
    adj_low = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Adjusted low'
    )
    adj_close = models.DecimalField(
        default=-1,
        max_digits=20,
        decimal_places=5,
        verbose_name=u'Adjusted close'
    )
    adj_factor = models.FloatField(
        default=0,
        verbose_name=u'Adjustment factor'
    )
    amount = models.FloatField(
        default=-1,
        verbose_name=u'成交金额 (000)'
    )
    vol = models.FloatField(
        verbose_name=u'Volume (000)'
    )
    flag_by_strategy = models.CharField(
        max_length=1,
        null=True,
        blank=True,
        default='U',
        verbose_name=u'Back testing flag'
    )
    val_by_strategy = models.FloatField(
        null=True,
        blank=True,
        default=0.0,
        verbose_name=u'Computed value based on a strategy'
    )
    peer_rank = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name=u'Ranking among peers'
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
        verbose_name=u"(Today's Close - Today's Open)/Today's Open*100"
    )
    relative_hl = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"Relative Position (H,L)"
    )
    relative_ma = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"Relative Position Moving Average"
    )
    lg_slope = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"Linear regression slope"
    )
    si = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"SI indicator"
    )
    cci = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"CCI indicator"
    )
    decycler_oscillator = models.FloatField(
        null=True,
        blank=True,
        default=None,
        verbose_name=u"Decycler oscillator"
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
        decimal_places=5,
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
            position: cost we paid when buying these stocks
            vol: qty
            close_position: price we took when selling these stocks

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
        decimal_places=5,
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
        verbose_name=u'Position close date'
    )
    simulation = models.ForeignKey(
        'MySimulationCondition'
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
        self._life_in_days()
        self.save()

    def _cost(self):
        """Cost to establish this position.

        cost = position price * holding volume
        """
        return self.position * self.vol
    cost = property(_cost)

    def _gain(self):
        """Realized gain/loss.

        Profit/loss realized by holding this stock till closing.
        """
        return (self.close_position - self.position) * self.vol
    gain = property(_gain)

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

    def _life_in_days(self):
        """Stock's life in days from its openning to closing.
        """
        if self.open_date and self.close_date:
            return (self.close_date - self.open_date).days
        else:
            return (self.last_updated_on - self.created).days
    life_in_days = property(_life_in_days)


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
        (2, "CI00*"),
        (3, "WIND 8821*"),
        (4, "China stock"),
        (5, 'WIND 2nd-tier sector'),
    )
    DATA_SORT_CHOICES = (
        (0, "ascending"),
        (1, "descending"),
    )
    STRATEGY_CHOICES = (
        (1, "S1 (by ranking)"),
        (2, "S2 (buy low sell high)"),
    )
    STRATEGY_VALUE_CHOICES = (
        (1, "Daily return"),
        (2, "Relative (H,L)"),
        (3, 'Relative Moving Avg'),
        # (4, 'CCI'),
        # (5, 'SI'),
        # (6, 'Linear Reg Slope'),
        # (7, 'Decycler Oscillator'),
    )
    data_source = models.IntegerField(
        choices=DATA_CHOICES,
        default=1
    )
    sector = models.ForeignKey(
        'MySector',
        null=True,
        blank=True,
        default=None,
        verbose_name=u'Data source sector'
    )
    strategy = models.IntegerField(
        choices=STRATEGY_CHOICES,
        default=1
    )
    strategy_value = models.IntegerField(
        choices=STRATEGY_VALUE_CHOICES,
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
                           "sector",
                           "strategy",
                           "strategy_value",
                           "data_sort",
                           "start",
                           "end",
                           "capital",
                           "per_trade",
                           "buy_cutoff",
                           "sell_cutoff")


class MySimulationResult(models.Model):
    """Simulation result model.

    This is a complex model because it will save the raw data
    from a simulation run so we can replay the entire simulation
    step by step.
    """
    description = models.TextField()
    on_dates = JSONField()  # date range
    asset = JSONField()  # assets
    cash = JSONField()  # cash
    equity = JSONField()
    portfolio = JSONField()
    transaction = JSONField()
    snapshot = JSONField()
    condition = models.OneToOneField('MySimulationCondition')

    def _num_of_buys(self):
        """Total number of buys.

        This is computed from individual buys.
        """
        return sum([len(t['buy']) for t in self.transaction])
    num_of_buys = property(_num_of_buys)

    def _num_of_sells(self):
        """Total number of sells.

        This is computed from individual sells.
        """
        return sum([len(t['sell']) for t in self.transaction])
    num_of_sells = property(_num_of_sells)

    def _asset_daily_return(self):
        """User asset's daily change in pcnt.

        This index shows how a user's asset fluctuates from day to day
        during simulation period.
        """
        return [1] + [(self.asset[x] - self.asset[x - 1]) / self.asset[x - 1] * 100 for x in range(1, len(self.asset))]
    asset_daily_return = property(_asset_daily_return)

    def _asset_cumulative_return(self):
        """Measures daily asset's return over T0's.

        This indes shows how assets swings comparing to simulation's T0.
        This can be viewed as an overall performance indicator over time.
        """
        cumulative = []
        t0 = self.asset[0]
        return [self.asset[x] / t0 for x in range(1, len(self.asset))]
    asset_cumulative_return = property(_asset_cumulative_return)

    def _asset_end_return(self):
        """Last's day's cumulative return.
        """
        return self.asset_cumulative_return[-1]
    asset_end_return = property(_asset_end_return)

    def _asset_max_return(self):
        """Best return % during simulation period.

        This indicator shows the maximum potential gain from
        applied strategy.
        """
        return max(self.asset_cumulative_return)
    asset_max_return = property(_asset_max_return)

    def _asset_min_return(self):
        """Worst return rate during simulation period.

        This shows the worst moment this strategy can yield.
        """
        return min(self.asset_cumulative_return)
    asset_min_return = property(_asset_min_return)

    def _asset_cumulative_return_mean(self):
        """Average gain.

        Numeric mean of gains. This indicates the likely gain one can achieve 
        by applying this strategy.	
        """
        return np.mean(self.asset_cumulative_return)
    asset_cumulative_return_mean = property(_asset_cumulative_return_mean)

    def _asset_cumulative_return_std(self):
        """Standard deviation of cumulative gains.

        This measures the risk of applied strategy using cumulative gain data.
        """
        return np.std(self.asset_cumulative_return)
    asset_cumulative_return_std = property(_asset_cumulative_return_std)

    def _equity_portfolio_gain_pcnt(self):
        """Equity gains from holding.

        This tracks equity gains from holding a perticular stock,
        not from trading it. It indicates
        how well equities were performing. This is completely determined by
        how well we picked stock, thus is a good indicator of applied strategy.
        """
        # We index [1:] so the pcnt is calculated using today's gain over
        # yesterday's equity value
        valid_equity = [float(s[1]['equity'])
                        for s in self.snapshot[:-1] if float(s[1]['equity'])]
        gain_from_hold = [] + [float(s[1]['gain']['hold'])
                               for s in self.snapshot[1:1 + len(valid_equity)]]
        return map(lambda x, y: x / y * 100, gain_from_hold, valid_equity)
    equity_portfolio_gain_pcnt = property(_equity_portfolio_gain_pcnt)

    def _equity_trade_gain_pcnt(self):
        """Equity gains from trading.

        This tracks gains from closing stocks based on applied strategy.
        This is influenced by both stock picking strategy and 
        trading strategy. So it measures the effect of both.
        """
        # We index [1:] so the pcnt is calculated using today's gain over
        # yesterday's equity value
        valid_equity = [float(s[1]['equity'])
                        for s in self.snapshot[:-1] if float(s[1]['equity'])]
        gain_from_sell = [] + [float(s[1]['gain']['sell'])
                               for s in self.snapshot[1:1 + len(valid_equity)]]
        return map(lambda x, y: x / y * 100, gain_from_sell, valid_equity)
    equity_trade_gain_pcnt = property(_equity_trade_gain_pcnt)

    def _equity_portfolio_life_in_days(self):
        """Equity life in days.

        We want to measure how long we usually hold a position. One strategy
        is to dictate how long we can hold a position.
        """
        life_in_days = [s[1]['gain']['sell']['life_in_days']
                        for s in self.snapshot if len(s[1]['gain']['sell'])]
        life_in_days = reduce(lambda x: [] + x, life_in_days)
        return (max(life_in_days), min(life_in_days), mean(life_in_days))
    equity_portfolio_life_in_days = property(_equity_portfolio_life_in_days)


class MyChenmin(models.Model):
    """Transient model.

    Used to import initial data.
    """
    executed_on = models.DateField(
        verbose_name=u'发生日期'
    )
    symbol = models.CharField(
        max_length=32,
        verbose_name=u'证券代码'
    )
    name = models.CharField(
        max_length=32,
        verbose_name=u'证券名称'
    )
    transaction_type = models.CharField(
        max_length=64,
        verbose_name=u'摘要'
    )
    price = models.FloatField(
        verbose_name=u'成交价格'
    )
    vol = models.IntegerField(
        verbose_name=u'成交股数'
    )
    total = models.IntegerField(
        verbose_name=u'成交金额'
    )


######################################################
#
#	RESTful API endpoints
#
#####################################################
from rest_framework import serializers, viewsets, filters

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
