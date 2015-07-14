#!/usr/bin/python  
# -*- coding: utf-8 -*-  

from django import forms
from django.conf import settings
from django.forms.models import modelformset_factory, inlineformset_factory
from django.contrib.contenttypes.generic import generic_inlineformset_factory
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, logout, login
from django.template import RequestContext
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy, resolve, reverse
from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.encoding import smart_text
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count,Max,Min,Avg

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
# protect the view with require_POST decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q,F
from django.template import loader, Context

# django-crispy-forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# django-filters
from django_filters import FilterSet, BooleanFilter
from django_filters.views import FilterView
import django_filters

# django emails
from django.core.mail import send_mail

# so what
import re,os,os.path,shutil,subprocess, testtools
import random,codecs,unittest,time, tempfile, csv, hashlib
from datetime import datetime as dt
from multiprocessing import Process, Queue
import simplejson as json
import googlemaps
from itertools import groupby
import urllib, lxml.html
from utility import MyUtility

from stock.models import *

###################################################
#
#	Common utilities
#
###################################################
def class_view_decorator(function_decorator):
	"""Convert a function based decorator into a class based decorator usable
	on class based Views.
	
	Can't subclass the `View` as it breaks inheritance (super in particular),
	so we monkey-patch instead.
	"""
	
	def simple_decorator(View):
		View.dispatch = method_decorator(function_decorator)(View.dispatch)
		return View
	
	return simple_decorator

###################################################
#
#	Static views
#
###################################################
class HomeView (TemplateView):
	template_name = 'intern/common/home_with_login_modal.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		user_auth_form = AuthenticationForm()
		user_registration_form = UserCreationForm()

		context['registration_form']=user_registration_form
		context['auth_form']=user_auth_form
		return context

###################################################
#
#	User views
#
###################################################
class LoginView(FormView):
	template_name = 'registration/login.html'
	success_url = reverse_lazy('stock_list')
	form_class = AuthenticationForm
	def form_valid(self,form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
		    login(self.request, user)
		    return super(LoginView, self).form_valid(form)
		else:
		    return self.form_invalid(form)

class LogoutView(TemplateView):
	template_name = 'registration/logged_out.html'
	def get(self,request):
		logout(request)
    	# Redirect to a success page.
		# messages.add_message(request, messages.INFO, 'Thank you for using our service. Hope to see you soon!')
		return HttpResponseRedirect (reverse_lazy('home'))

class UserRegisterView(FormView):
	template_name = 'registration/register_form.html'
	form_class = UserCreationForm
	success_url = reverse_lazy('login')
	def form_valid(self,form):
		user_name = form.cleaned_data['username']
		password = form.cleaned_data['password2']
		if len(User.objects.filter(username = user_name))>0:
			return self.form_invalid(form)
		else:
			user = User.objects.create_user(user_name, '', password)			
			user.save()

			return super(UserRegisterView,self).form_valid(form)

###################################################
#
#	MyApplication views
#
###################################################
class UserProfileView(TemplateView):
	template_name='stock/user/profile.html'
	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		if self.request.user.is_authenticated():
			user_profile,created = MyUserProfile.objects.get_or_create(owner=self.request.user)
		return context

	def post(self,request):
		pe_threshold = request.POST['pe'].strip()
		per_trade_total = request.POST['per_trade_total'].strip()
		exit_pcnt = request.POST['exit_pcnt'].strip()
		
		# get user property obj
		user_profile,created = MyUserProfile.objects.get_or_create(owner=request.user)
		user_profile.pe_threshold = pe_threshold
		try: user_profile.per_trade_total = float(per_trade_total)
		except: pass # no change
		try: user_profile.exit_percent = int(exit_pcnt)
		except: pass
		user_profile.save()

		# refresh current page, whatever it is.
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

class MyStockListFilter (FilterSet):
	class Meta:
		model = MyStock
		fields = {
				'company_name':['contains'],
				'symbol':['contains'],
				'is_in_play':['exact'],
				# 'sponsor__is_sas_paying_student_fees':['exact'],
				# 'sponsor__is_to_return_balance':['exact']
				}

class MyStockList (FilterView):
	template_name = 'stock/stock/list.html'
	paginate_by = 500
	
	def get_filterset_class(self):
		return MyStockListFilter

from tasks import stock_monitor_yahoo_consumer,stock_monitor_yahoo_consumer2
@class_view_decorator(login_required)
class MyStockUpdate(TemplateView):
	template_name = ''

	def post(self,request):
		step = 100
		total = 500
		symbols = MyStock.objects.all().values_list('symbol',flat=True)
		for i in xrange(total/step):	
			stock_monitor_yahoo_consumer.delay(','.join(symbols[i*step:(i*step+step)]))
			stock_monitor_yahoo_consumer2.delay(','.join(symbols[i*step:(i*step+step)]))

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')

@class_view_decorator(login_required)
class MyStockHeatPrevChange(ListView):
	template_name = 'stock/stock/list_heat_prev_change.html'
	paginate_by = 250

	def get_queryset(self):
		return MyStock.objects.in_heat(self.request.user)[:250]

@class_view_decorator(login_required)
class MyStockHeatSpread(ListView):
	template_name = 'stock/stock/list_heat_spread.html'
	paginate_by = 250

	def get_queryset(self):
		return MyStock.objects.in_heat(self.request.user).order_by('spread')

@class_view_decorator(login_required)
class MyStockHeatDayChange(ListView):
	template_name = 'stock/stock/list_heat_day_change.html'
	paginate_by = 250

	def get_queryset(self):
		return MyStock.objects.in_heat(self.request.user).filter(day_change__gt=0)

@class_view_decorator(login_required)
class MyStockHeatVolOverFloat(ListView):
	template_name = 'stock/stock/list_heat_vol_over_float.html'
	paginate_by = 250

	def get_queryset(self):
		return MyStock.objects.in_heat(self.request.user).order_by('vol_over_float')

@class_view_decorator(login_required)
class MyStockTrend(TemplateView):
	template_name = 'stock/stock/trend.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['up_up'] = MyStock.objects.filter(prev_change__gt=0,day_change__gt=0)
		context['down_up'] = MyStock.objects.filter(prev_change__lt=0,day_change__gt=0)
		context['up_down'] = MyStock.objects.filter(prev_change__gt=0,day_change__lt=0)
		context['down_down'] = MyStock.objects.filter(prev_change__lt=0,day_change__lt=0)
		return context