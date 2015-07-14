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
from localflavor.us.forms import USPhoneNumberField

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

	def in_heat(self,user,top_count=500):
		# data = self.filter_by_user_pe_threshold(user).filter(prev_change__gt=0,day_open__lte=F('prev_close')).order_by('-prev_change')[:top_count]
		data = self.filter_by_user_pe_threshold(user).filter(prev_change__gt=0).order_by('-prev_change')[:top_count]
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

	def __unicode__(self):
		return '%s (%s)'%(self.symbol,self.company_name)

@receiver(pre_save,sender=MyStock)
def day_change_handler(sender, **kwargs):
	instance = kwargs.get('instance')
	if instance.id: 
		original = MyStock.objects.get(id=instance.id)

		# if we are changing into a new day, update prev_ fields
		if dt.today() > original.last_update_time.date():
			# set prev values
			instance.prev_open = instance.day_open
			instance.prev_high = instance.day_high
			instance.prev_low = instance.day_low
			instance.prev_close = instance.last
			instance.prev_vol = instance.vol
			instance.prev_change = (instance.prev_open-instance.prev_close)/instance.prev_open*100

			# reset current day values
			instance.day_open = 0
			instance.last = 0
			instance.vol = 0
			instance.ask = instance.bid = 0.0
			instance.day_range = ''

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