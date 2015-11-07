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
from annoying.fields import JSONField # django-annoying
from django.db.models import Q,F
from datetime import datetime as dt
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from decimal import Decimal
from django.core.validators import MaxValueValidator, MinValueValidator
from math import fabs

class MyBaseModel (models.Model):
	# fields
	hash = models.CharField (
		max_length = 256, # we don't expect using a hash more than 256-bit long!
		null = True,
		blank = True,
		default = '',
		verbose_name = u'MD5 hash'
	)
		
	# basic value fields
	name = models.CharField(
			default = None,
			max_length = 128,
			verbose_name = u'名称'
		)
	description = models.TextField (
			null=True, 
			blank=True,
			verbose_name = u'描述'
		)
	
	# help text
	help_text = models.CharField (
			max_length = 64,
			null = True,
			blank = True,
			verbose_name = u'帮助提示'
		)

	# attachments
	attachments = GenericRelation('Attachment')
	
	# this is an Abstract model
	class Meta:
		abstract=True

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
			default = '',
			max_length = 16,
			verbose_name = u'Tag'
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
	created_by = models.ForeignKey (
		User,
		blank = True,
		null = True,
		default = None,
		verbose_name = u'创建用户',
		help_text = ''
	)
		
	# basic value fields
	name = models.CharField(
		default = 'default name',
		max_length = 64,
		verbose_name = u'附件名称'
	)
	description = models.CharField (
		max_length = 64,
		default = 'default description',
		verbose_name = u'附件描述'
	)
	file = models.FileField (
		upload_to = '%Y/%m/%d',
		verbose_name = u'附件',
		help_text = u'附件'
	)	

	def __unicode__(self):
		return self.file.name

class AttachmentForm(ModelForm):
	class Meta:
		model = Attachment
		fields = ['description','file']

######################################################
#
#	App specific models
#
#####################################################
class MyStockCustomManager(models.Manager):
	def filter_by_user_pe_threshold(self,user):
		data = self.get_queryset()

		# get user profile
		user_profile,created = MyUserProfile.objects.get_or_create(owner = user)
		pe_low = int(user_profile.pe_threshold.split('-')[0])
		pe_high = int(user_profile.pe_threshold.split('-')[1])
		return data.filter(pe__gte=pe_low,pe__lte=pe_high)

	def in_heat(self,user):
		# data = self.filter_by_user_pe_threshold(user).filter(prev_change__gt=0,day_open__lte=F('prev_close')).order_by('-prev_change')[:top_count]
		data = self.filter_by_user_pe_threshold(user).filter(prev_change__gt=0).order_by('-prev_change')
		return data

class MySector(models.Model):
	parent = models.ForeignKey(
		'self',
		null = True,
		blank = True,
		default = None,
		verbose_name = u'Parent sector'
	)
	code = models.CharField(
		max_length = 8,
		verbose_name = u'Sector code'
	)
	source = models.CharField(
		max_length = 32,
		verbose_name = u'Definition source'
	)
	name = models.CharField(
		max_length = 32,
		null = True,
		blank = True	
	)
	description = models.TextField(
		null = True,
		blank = True
	)
	stocks = models.ManyToManyField('MyStock')
	
class MyStock(models.Model):
	# custom managers
	# Note: the 1st one defined will be taken as the default!
	objects = MyStockCustomManager()

	company_name = models.CharField(
		max_length = 128,
		null = True,
		blank = True,
		verbose_name = u'Company name'
	)
	symbol = models.CharField(
		max_length = 8,
		verbose_name = u'Stock symbol'
	)
	sector = models.CharField(
		max_length = 64,
		default = 'unknown',
		verbose_name = u'Sector name'
	)
	is_sp500 = models.BooleanField(
		default = False,
		verbose_name = u'Is a SP500 stock'
	)
	is_china_stock = models.BooleanField(
		default = False,
		verbose_name = u'Is a China stock'
	)
	prev_close = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Prev day closing price'
	)
	prev_open = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Prev day opening price'
	)
	prev_high = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Prev day highest price'
	)	
	prev_low = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Prev day lowest price'
	)
	prev_vol = models.IntegerField(
		default = 0,
		verbose_name = u'Prev day volume'
	)	
	day_open = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Today opening price'
	)
	pe = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'P/E'
	)
	bid = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Bid price'
	)	
	ask = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Ask price'
	)	
	vol = models.FloatField(		
		default = 0.0,
		verbose_name = u'Volume (in 000)'
	)
	floating_share = models.FloatField(		
		default = 0.0,
		verbose_name = u'Floating share(in million)'
	)
	day_high = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Day high'		
	)
	day_low = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Day low'		
	)

	last = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Spot price'
	)
	last_update_time = models.DateTimeField(
		null = True,
		blank = True,
		auto_now=True,
		verbose_name = u'Spot sample time'
	)
	is_in_play = models.BooleanField(
		default = False,
		verbose_name = u'Has pending position'
	)
	prev_change = models.FloatField(
		default = 0.0,
		verbose_name = u'Prev day change (%)'
	)
	day_change = models.FloatField(
		default = 0.0,
		verbose_name = u'Today change(%)'
	)
	spread = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 0.0,
		verbose_name = u'Bid-ask spread'
	)
	vol_over_float = models.FloatField(
		default = 0.0,
		verbose_name = u'Vol/floating shares (%)'
	)
	week_adjusted_close = models.TextField(
		default = '',
		verbose_name = u'1-week adjusted closing price'
	)
	month_adjusted_close = models.TextField(
		default = '',
		verbose_name = u'1-month adjusted closing price'
	)	
	fib_weekly_adjusted_close = models.TextField(
		default = '',
		verbose_name = u'Fibonacci timezone adjusted closing price'
	)	
	fib_daily_adjusted_close = models.TextField(
		default = '',
		verbose_name = u'Fibonacci timezone adjusted closing price'
	)		
	fib_weekly_score = models.FloatField(
		default = 0,
		verbose_name = u'Weighed sum of weekly adj close price'
	)
	fib_daily_score = models.FloatField(
		default = 0,
		verbose_name = u'Weighed sum of daily adj close price'		
	)

	def _oneday_change(self):
		return (self.last-self.day_open)/self.day_open*Decimal(100)
	oneday_change = property(_oneday_change)

	def _twoday_change(self):
		return (self.last-self.prev_open)/self.prev_open*Decimal(100)
	twoday_change = property(_twoday_change)

	def _week_change(self):
		vals = self.week_adjusted_close.split(',')
		return (Decimal(vals[-1])-Decimal(vals[0]))/Decimal(vals[0])*Decimal(100)
	week_change = property(_week_change)

	def _month_change(self):
		vals = self.month_adjusted_close.split(',')
		return (Decimal(vals[-1])-Decimal(vals[0]))/Decimal(vals[0])*Decimal(100)
	month_change = property(_month_change)

	def _trend_is_consistent_gain(self):
		if self.oneday_change>0 and self.twoday_change>0 and self.week_change>0 and self.month_change>0:
			return True
		else: return False
	trend_is_consistent_gain = property(_trend_is_consistent_gain)

	def _trend_is_consistent_loss(self):
		if self.oneday_change<0 and self.twoday_change<0 and self.week_change<0 and self.month_change<0:
			return True
		else: return False
	trend_is_consistent_loss = property(_trend_is_consistent_loss)

	def _fib_weekly_score_pcnt(self):
		return self.fib_weekly_score/float(self.last)*100
	fib_weekly_score_pcnt = property(_fib_weekly_score_pcnt)

	def _fib_daily_score_pcnt(self):
		return self.fib_daily_score/float(self.last)*100
	fib_daily_score_pcnt = property(_fib_daily_score_pcnt)

	def __unicode__(self):
		return '%s (%s)'%(self.symbol,self.company_name)

@receiver(pre_save,sender=MyStock)
def stock_update_handler(sender, **kwargs):
	instance = kwargs.get('instance')
	if instance.id: 
		original = MyStock.objects.get(id=instance.id)

		# spot price changed
		if original.last != instance.last and instance.day_open:
			# update day_change
			instance.day_change = (instance.last-instance.day_open)/instance.day_open*Decimal(100)

		# if ask or bid changed
		if original.ask!=instance.ask or original.bid!=instance.bid:
			instance.spread = instance.ask-instance.bid

		# if vol changed
		if original.vol != instance.vol and instance.float_share:
			instance.vol_over_float = instance.vol/instance.float_share/10

class MyStockHistorical(models.Model):
	stock = models.ForeignKey(
		'MyStock',
		verbose_name = u'Stock'
	)
	date_stamp = models.DateField(
		verbose_name = u'Date'
	)
	open_price = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		verbose_name = u'Open'
	)
	high_price = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'High'
	)
	low_price = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'Low'
	)	
	close_price = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'Close'
	)
	adj_open = models.DecimalField(
		default = -1,
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'Adjusted open'
	)
	adj_high = models.DecimalField(
		default = -1,
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'Adjusted high'
	)
	adj_low = models.DecimalField(
		default = -1,
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'Adjusted low'
	)			
	adj_close = models.DecimalField(
		default = -1,
		max_digits = 20,
		decimal_places = 5,			
		verbose_name = u'Adjusted close'
	)
	adj_factor = models.FloatField(
		default = 0,
		verbose_name = u'Adjustment factor'
	)
	amount = models.FloatField(
		default = -1,		
		verbose_name = u'成交金额 (000)'		
	)	
	vol = models.FloatField(
		verbose_name = u'Volume (000)'
	)
	flag_by_strategy = models.CharField(
		max_length = 1,
		null = True,
		blank = True,		
		default='U',
		verbose_name = u'Back testing flag'
	)
	val_by_strategy = models.FloatField(
		null = True,
		blank = True,
		default = 0.0,
		verbose_name = u'Computed value based on a strategy'
	)
	peer_rank = models.IntegerField(
		null = True,
		blank = True,
		default = 0,
		verbose_name = u'Ranking among peers'
	)
	status = models.IntegerField(
		default = -1,
		verbose_name = u'Stock trading status, eg. stopped trading on that day'
	)

	# pre-computed index values
	daily_return = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"(Today's Close - Today's Open)/Today's Open*100"
	)
	relative_hl = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"Relative Position (H,L)"
	)
	relative_ma = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"Relative Position Moving Average"
	)	
	lg_slope = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"Linear regression slope"
	)
	si = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"SI indicator"
	)
	cci = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"CCI indicator"
	)
	decycler_oscillator = models.FloatField(
		null = True,
		blank = True,
		verbose_name = u"Decycler oscillator"
	)

	# live computed properties
	def _avg_price(self):
		if self.vol and self.amount: return Decimal(self.amount)/Decimal(self.vol)
		else: return None
	avg_price = property(_avg_price)

	class Meta:
		unique_together = ('stock','date_stamp')
		index_together = ['stock', 'date_stamp']

class MyUserProfile(models.Model):	
	owner = models.OneToOneField (
		User,
		default = None,
		verbose_name = u'用户',
		help_text = ''
	)
	per_trade_total = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,		
		default = 1000.0,
		verbose_name = u'Per trade dollar amount'
	)
	pe_threshold = models.CharField(
		max_length = 16,
		default = '20-100',
		verbose_name = u'P/E threshold'
	)
	cash = models.DecimalField(
		max_digits = 20,
		decimal_places = 2,
		default = 10000,
		verbose_name = u'Account balance'
	)

	def _equity(self):
		pos = [p.total for p in MyPosition.objects.filter(user=self.owner,is_open = True)]
		return sum(pos)
	equity = property(_equity)

	def _asset(self):
		return self.cash+self.equity
	asset = property(_asset)

class MyPosition(models.Model):
	created = models.DateTimeField(
		auto_now_add=True,
	)
	user = models.ForeignKey(User)
	stock = models.ForeignKey(
		'MyStock',
		verbose_name = u'Stock'
	)
	position = models.DecimalField(
		max_digits = 20,
		decimal_places = 4,
		verbose_name = u'We paid'		
	)
	vol = models.DecimalField(
		max_digits = 20,
		decimal_places = 4,		
		default = 0,
		verbose_name = u'Trade vol'
	)
	is_open = models.BooleanField(
		default = True,
		verbose_name = u'Is position open'
	)
	last_updated_on = models.DateTimeField(
		auto_now = True
	)
	close_position = models.DecimalField(
		max_digits = 20,
		decimal_places = 5,
		default = 0.0,
		verbose_name = u'We closed at'
	)
	open_date = models.DateField(
		null = True,
		blank = True,
		verbose_name = u'Position open date'
	)
	close_date = models.DateField(
		null = True,
		blank = True,
		verbose_name = u'Position close date'
	)
	simulation = models.ForeignKey(
		'MySimulationCondition'
	)
	def add(self,user,price,vol,source='simulation',on_date=None):
		"""
		Utility function to buy or sell.
		
		If vol > 0: buy; < 0: sell.
		If updated vol == 0, this position will be marked "closed".

		User profile's cash will be updated:
		if buy: cash -= price * vol
		if sell: cash += price * vol
		"""

		# new position = weighted avg
		self.position = (self.position*self.vol+price*vol)/(self.vol+vol)
		self.vol += vol
		if not self.vol: self.is_open = False
		if on_date: self.open_date = on_date
		else: self.open_date = dt.now().date()		
		self.save()

	def close(self,user,price,on_date=None):
		"""
		Close position.
		"""
		self.close_position = price
		self.is_open = False
		if on_date: self.close_date = on_date
		else: self.close_date = dt.now().date()
		self._life_in_days()
		self.save()		

	def _cost(self):
		return self.position*self.vol
	cost = property(_cost)
	
	def _gain(self):
		return (self.close_position - self.position)*self.vol
	gain = property(_gain)

	def _potential_gain(self):
		return (self.stock.last - self.position)*self.vol
	potential_gain = property(_potential_gain)

	def _to_last_pcnt(self):
		return (self.stock.last-self.position)/self.position*100.0
	to_last_pcnt = property(_to_last_pcnt)

	def _total(self):
		return self.stock.last * self.vol
	total = property(_total)		

	def _elapse_in_days(self):
		return (dt.now().date()-self.created.date()).days
	elapse_in_days = property(_elapse_in_days)

	def _life_in_days(self):
		if self.open_date and self.close_date:
			return (self.close_date - self.open_date).days
		else: return (self.last_updated_on-self.created).days
	life_in_days = property(_life_in_days)	

@receiver(pre_save,sender=MyPosition)
def day_change_handler(sender, **kwargs):
	instance = kwargs.get('instance')
	if instance.close_date: instance.is_open = False
	if instance.is_open:
		stock = MyStock.objects.get(id=instance.stock.id)
		if not stock.is_in_play:
			stock.is_in_play = True
			stock.save()

class MySimulationCondition(models.Model):
	DATA_CHOICES = (
		(1, "S&P500"),
		(2, "CI00"),
		(3, "WIND 8821"), 
		(4, "China stock"),    
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
		choices = DATA_CHOICES,
		default = 1
	)
	strategy = models.IntegerField(
		choices = STRATEGY_CHOICES,
		default = 1
	)
	strategy_value = models.IntegerField(
		choices = STRATEGY_VALUE_CHOICES,
		default = 1,
		verbose_name = u"Strategy value"
	)
	data_sort = models.IntegerField(
		choices = DATA_SORT_CHOICES,
		default = 2,
		verbose_name = u"Sort order"
	)
	start = models.DateField (
		default = "2014-01-01",
		verbose_name = u'Start date'
	)
	end = models.DateField (
		default = "2014-01-10",
		verbose_name = u'End date',
	)
	capital = models.IntegerField(
		default = 100000,
		verbose_name = u"Starting cash"
	) 
	per_trade = models.IntegerField(
		default = 10000,
		verbose_name = u"Per trade amount"
	)      
	buy_cutoff = models.IntegerField(
		default = 25,
		validators = [
			MaxValueValidator(100),
			MinValueValidator(0)
		],
		verbose_name = "Buy cutoff (%)"
	)
	sell_cutoff = models.IntegerField(
		default = 75,
		validators = [
			MaxValueValidator(100),
			MinValueValidator(0)
		],
		verbose_name = "Sell cutoff (%)"
	)

	def __unicode__(self):
		return '%s-%s-%s (%d-%d), %s - %s' %(self.get_data_source_display(), 
			self.get_strategy_display(), 
			self.get_strategy_value_display(),
			self.buy_cutoff,
			self.sell_cutoff,
			self.start,
			self.end)

class MySimulationResult(models.Model):
	description = models.TextField()
	on_dates = JSONField()
	asset = JSONField()
	cash = JSONField()
	equity = JSONField()
	portfolio = JSONField()
	transaction = JSONField()
	snapshot = JSONField()
	condition = models.OneToOneField('MySimulationCondition')

class MyChenmin(models.Model):
	executed_on = models.DateField(
		verbose_name = u'发生日期'
	)
	symbol = models.CharField(
		max_length = 32,
		verbose_name = u'证券代码'
	)
	name = models.CharField(
		max_length = 32,
		verbose_name = u'证券名称'
	)
	transaction_type = models.CharField(
		max_length = 64,
		verbose_name = u'摘要'
	)
	price = models.FloatField(
		verbose_name = u'成交价格'
	)
	vol = models.IntegerField(
		verbose_name = u'成交股数'
	)
	total = models.IntegerField(
		verbose_name = u'成交金额'
	)


######################################################
#
#	RESTful API endpoints
#
#####################################################

from rest_framework import serializers, viewsets,filters

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