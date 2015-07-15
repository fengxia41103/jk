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
	prev_close = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Prev day closing price'
	)
	prev_open = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Prev day opening price'
	)
	prev_high = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Prev day highest price'
	)	
	prev_low = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Prev day lowest price'
	)
	prev_vol = models.IntegerField(
		default = 0,
		verbose_name = u'Prev day volume'
	)	
	day_open = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Today opening price'
	)
	pe = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'P/E'
	)
	bid = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Bid price'
	)	
	ask = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Ask price'
	)	
	vol = models.FloatField(		
		default = 0.0,
		verbose_name = u'Volume (in 000)'
	)
	float_share = models.FloatField(		
		default = 0.0,
		verbose_name = u'Float share(in million)'
	)
	day_high = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Day high'		
	)
	day_low = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 0.0,
		verbose_name = u'Day low'		
	)

	last = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
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
		decimal_places = 15,		
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
	fib_adjusted_close = models.TextField(
		default = '',
		verbose_name = u'Fib interval adjusted closing price'
	)	

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
		if self.twoday_change>0 and self.week_change>0 and self.month_change>0:
			return True
		else: return False
	trend_is_consistent_gain = property(_trend_is_consistent_gain)

	def _trend_is_consistent_loss(self):
		if self.twoday_change<0 and self.week_change<0 and self.month_change<0:
			return True
		else: return False
	trend_is_consistent_loss = property(_trend_is_consistent_loss)

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

class MyUserProfile(models.Model):	
	owner = models.OneToOneField (
		User,
		default = None,
		verbose_name = u'用户',
		help_text = ''
	)
	per_trade_total = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,		
		default = 1000.0,
		verbose_name = u'Per trade dollar amount'
	)
	pe_threshold = models.CharField(
		max_length = 16,
		default = '20-100',
		verbose_name = u'P/E threshold'
	)
	exit_percent = models.IntegerField(
		default = 2,
		verbose_name = u'Percentage of exit over buy-in price'
	)

class MyPosition(models.Model):
	created = models.DateTimeField(
		auto_now_add=True,
	)
	stock = models.ForeignKey(
		'MyStock',
		verbose_name = u'Stock'
	)
	position = models.DecimalField(
		max_digits = 20,
		decimal_places = 15,
		verbose_name = u'We paid'		
	)
	exit_bid = models.DecimalField(		
		max_digits = 20,
		decimal_places = 15,				
		verbose_name = u'Sell at'
	)
	vol = models.IntegerField(
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

	def _total(self):
		return self.exit * self.vol
	total = property(_total)		

	def _elapse_in_days(self):
		return (dt.now().date()-self.created.date()).days
	elapse_in_days = property(_elapse_in_days)

	def _life_in_days(self):
		return (self.last_updated_on-self.created).days
	life_in_days = property(_life_in_days)	

@receiver(post_save,sender=MyPosition)
def day_change_handler(sender, **kwargs):
	instance = kwargs.get('instance')
	stock = MyStock.objects.get(id=instance.stock)
	stock.is_in_play = True
	stock.save()