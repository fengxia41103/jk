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
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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
from numpy import mean, std 
from utility import MyUtility

from stock.forms import DateSelectionForm
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
	success_url = reverse_lazy('trend_2day_loss')
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
class MyStockTrendTransition(TemplateView):
	template_name = 'stock/stock/trend_2day_transition.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['up_up'] = MyStock.objects.filter(prev_change__gt=0,day_change__gt=0)
		context['down_up'] = MyStock.objects.filter(prev_change__lt=0,day_change__gt=0)
		context['up_down'] = MyStock.objects.filter(prev_change__gt=0,day_change__lt=0)
		context['down_down'] = MyStock.objects.filter(prev_change__lt=0,day_change__lt=0)
		return context

@class_view_decorator(login_required)
class MyStockTrendGain(TemplateView):
	template_name = 'stock/stock/trend_gain.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['direction'] = 'Gain'
		context['object_list'] = MyStock.objects.filter(prev_open__lt=F('last'))
		return context

@class_view_decorator(login_required)
class MyStockTrendLoss(TemplateView):
	template_name = 'stock/stock/trend_gain.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['direction'] = 'Loss'
		context['object_list'] = MyStock.objects.filter(prev_open__gt=F('last'))
		return context	

@class_view_decorator(login_required)
class MyStockTrendConsistentGain(TemplateView):
	template_name = 'stock/stock/trend_gain.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['direction'] = 'Consistent gain'
		context['object_list']=filter(lambda x: x.trend_is_consistent_gain, MyStock.objects.filter(prev_open__lt=F('last')))

		return context	

@class_view_decorator(login_required)
class MyStockTrendConsistentLoss(TemplateView):
	template_name = 'stock/stock/trend_gain.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		context['direction'] = 'Consistent loss'
		context['object_list']=filter(lambda x: x.trend_is_consistent_loss, MyStock.objects.filter(prev_open__gt=F('last')))

		return context

@class_view_decorator(login_required)
class MyStockPosition(TemplateView):
	template_name = 'stock/stock/position.html'
	def post(self,request):
		stock = MyStock.objects.get(id=int(self.request.POST['obj_id']))		
		pos_open = MyPosition.objects.filter(stock=stock,user=self.request.user, is_open=True)
		
		content = loader.get_template(self.template_name)
		html= content.render(Context({'pos_open':pos_open,'obj_id':stock.id}))

		return HttpResponse(json.dumps({'html':html}), 
			content_type='application/javascript')	

@class_view_decorator(login_required)
class MyStockTransaction(TemplateView):
	template_name = ''	

	def post(self,request):
		stock = MyStock.objects.get(id=int(self.request.POST['obj_id']))
		transaction_type = self.request.POST['type']

		# get user property obj
		user_profile,created = MyUserProfile.objects.get_or_create(owner=request.user)

		# establish a new position
		if transaction_type == 'bid': # buy 1
			vol = int(user_profile.per_trade_total/stock.last)
			pos = MyPosition(stock=stock,position=stock.last,vol=vol,user=request.user)
			user_profile.cash -= pos.vol*pos.position

			user_profile.save()
			pos.save()

		elif transaction_type == 'ask': # sell 1, FIFO
			pos = MyPosition.objects.filter(user=request.user,stock=stock,is_open=True).order_by('created')[0]
			pos.is_open = False
			pos.close_position = stock.last
			user_profile.cash += pos.vol * pos.close_position

			user_profile.save()
			pos.save()
		
		elif transaction_type == 'close': # close positions
			for pos in MyPosition.objects.filter(user=request.user,stock=stock,is_open=True):
				pos.is_open = False
				pos.close_position = stock.last
				user_profile.cash += pos.vol * pos.close_position
				pos.save()

		# update records
		user_profile.save()

		return HttpResponse(json.dumps({'status':'ok'}), 
			content_type='application/javascript')

from statistics import mean
@class_view_decorator(login_required)
class UserPositionList(ListView):
	template_name = 'stock/stock/position_list.html'	

	def get_queryset(self):		
		data = []
		stocks = MyPosition.objects.filter(user=self.request.user,is_open = True).values_list('stock',flat=True)
		for s in stocks:
			tmp={'id':s,'stock':MyStock.objects.get(id=s)}
			tmp['potential_gain'] = sum([a.potential_gain for a in MyPosition.objects.filter(user=self.request.user,is_open=True,stock=s)])
			tmp['life'] = mean([a.elapse_in_days for a in MyPosition.objects.filter(user=self.request.user,is_open=True,stock=s)])
			tmp['avg_cost'] = sum([a.total for a in MyPosition.objects.filter(user=self.request.user,is_open=True,stock=s)])/sum([a.vol for a in MyPosition.objects.filter(user=self.request.user,is_open=True,stock=s)])
			data.append(tmp)			
		return data

@class_view_decorator(login_required)
class MyStockCandidateList(ListView):
	template_name ='stock/stock/trend_gain.html'

	def get_context_data(self, **kwargs):
		context = super(ListView, self).get_context_data(**kwargs)
		context['direction'] = 'Candidate'
		return context		

	def get_queryset(self):
		stocks = MyStock.objects.all()
		return filter(lambda x: x.trend_is_consistent_loss and # has been on down curve
			(x.oneday_change < -2 or x.twoday_change < -4) and # 2-day drop greater than 4%
			x.fib_weekly_score_pcnt>0 and # weekly trending up
			x.fib_daily_score_pcnt>0 and  # daily trending up
			x.fib_weekly_score_pcnt+float(x.oneday_change)>0 and # weekly trending up > drops
			x.fib_weekly_score_pcnt+float(x.twoday_change)>0 and
			x.fib_daily_score_pcnt+float(x.oneday_change)>0 and # daily trending up > drops
			x.fib_daily_score_pcnt+float(x.twoday_change)>0,
			stocks)

from nltk import FreqDist
@class_view_decorator(login_required)
class MyStockStrategy1Detail(TemplateView):
	model = MyStockHistorical
	template_name ='stock/backtesting/s1_detail.html'

	def occurrences(self, haystack, needle):
		return sum(haystack[i:i+len(needle)] == needle for i in xrange(len(haystack)-len(needle)+1))

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		stock = MyStock.objects.get(symbol__iexact=self.kwargs['symbol'])		
		context['stock'] = stock

		histories = MyStockHistorical.objects.filter(stock=stock).order_by('date_stamp')
		histories = tmp = ''.join([h.flag_by_strategy for h in histories])
		tmp = re.sub('[U]+','U',tmp)
		tmp = re.sub('[G]+','G',tmp)
		tmp = re.sub('[L]+','L',tmp)
		context['flag_by_strategy'] = histories

		# probabilities
		total_sample = len(tmp)-5+1
		context['prob_ggg'] = self.occurrences(tmp,'GUGUG')
		context['prob_ggl'] = self.occurrences(tmp,'GUGUL')
		context['prob_glg'] = self.occurrences(tmp,'GULUG')
		context['prob_gll'] = self.occurrences(tmp,'GULUL')
		context['prob_lgg'] = self.occurrences(tmp,'LUGUG')
		context['prob_lgl'] = self.occurrences(tmp,'LUGUL')
		context['prob_llg'] = self.occurrences(tmp,'LULUG')
		context['prob_lll'] = self.occurrences(tmp,'LULUL')
		context['prob_conseq_u'] = FreqDist([str(len(x)) for x in re.findall('[U]+',histories)]).most_common(10)
		context['prob_conseq_g'] = FreqDist([str(len(x)) for x in re.findall('[G]+',histories)]).most_common(10)
		context['prob_conseq_l'] = FreqDist([str(len(x)) for x in re.findall('[L]+',histories)]).most_common(10)
		context['ending_g_over_l'] = sum([context['prob_ggg'],context['prob_glg'],context['prob_lgg'],context['prob_llg']])*1.0/sum([context['prob_ggl'],context['prob_gll'],context['prob_lgl'],context['prob_lll']])

		context['peers'] = MyStock.objects.all().values_list('symbol',flat=True)
		return context	

@class_view_decorator(login_required)
class MyStockStrategy2Detail(TemplateView):
	model = MyStockHistorical
	template_name ='stock/backtesting/s2_detail.html'

	def get_context_data(self, **kwargs):
		context = super(TemplateView, self).get_context_data(**kwargs)
		stock = MyStock.objects.get(symbol__iexact=self.kwargs['symbol'])		
		context['stock'] = stock

		context['year'] = selected_year = self.kwargs['year']
		histories = MyStockHistorical.objects.filter(stock=stock,date_stamp__year=selected_year).order_by('date_stamp')
		context['ranks'] = [int(h.peer_rank) for h in histories]

		context['peers'] = [{'symbol':s,'url':reverse('backtesting_2_detail',kwargs={'symbol':s,'year':selected_year})} for s in MyStock.objects.filter(is_sp500=False,symbol__startswith="CI").values_list('symbol',flat=True)]
		return context

def simulate_trading(user,data,historicals,capital=100000,per_buy=1000,buy_cutoff=0.25,sell_cutoff=0.25):
	"""
	@param user: request.user
	@param data: a list of dict, [{'on_date':date obj, 'ranks':['symbol 1','symbol 2']}]
	@param capital: starting cash amount
	@param per_buy: per trade total amount, vol = per_buy/stock_price
	@param buy_cutoff: symbols[: cutoff * total sample number] -> buy these
	@param sell_cutoff: symbols[cutoff * total sample number: ] -> sell these

	@return: {date: asset value}
	@rtype: dict
	"""
	for h in MyPosition.objects.all(): h.delete()
	capital = user.myuserprofile.cash = 100000
	user.myuserprofile.save()

	# asset simulation result
	assets = {}
	
	# trading
	for d in data:
		print d['on_date'].isoformat()

		positions = MyPosition.objects.filter(is_open=True).values_list('stock__symbol',flat=True)		
		total_symbols = len(d['ranks'])

		# buy if within buy_cutoff
		for sym in d['ranks'][:int(total_symbols*buy_cutoff):]:
			if sym in positions: continue # already in portfolio, hold

			# we buy, assuming knowing the ranking based on OPEN price
			# so we buy at mean(high,low) on that date
			his = historicals.get(stock__symbol=sym,date_stamp=d['on_date'])
			stock = MyStock.objects.get(symbol=sym)
			stock.last = target_price = his.high_price # assuming we buy at daily high
			stock.save()
			pos = MyPosition(
				stock = stock,
				user = user,
				position = target_price, # buy
				vol = per_buy/target_price,
				open_date = d['on_date'])
			pos.save()

			profile = MyUserProfile.objects.get(owner = user)
			profile.cash -= pos.vol*pos.position
			profile.save()
			print 'create: ',sym, profile.cash

		# sell if outside sell_cutoff
		for sym in filter(lambda x: x in positions, d['ranks'][int(total_symbols*sell_cutoff):]):
			his = historicals.get(stock__symbol=sym,date_stamp=d['on_date'])
			target_price = his.low_price # assuming we sell at daily low				
			MyPosition.objects.get(stock__symbol=sym,is_open=True).close(user,target_price,on_date=d['on_date'])
			profile = MyUserProfile.objects.get(owner = user)
			print 'close: ',sym, profile.cash

		assets[d['on_date']] = profile.asset
	return assets

@class_view_decorator(login_required)
class MyStockStrategy2List(FormView):
	template_name = 'stock/backtesting/s2_list.html'
	form_class = DateSelectionForm
	success_url = '/thanks/'

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.
		start = form.cleaned_data['start']
		end = form.cleaned_data['end']

		stocks = MyStock.objects.filter(symbol__startswith="CI00")
		histories = MyStockHistorical.objects.filter(stock__in=stocks,date_stamp__range=[start,end]).order_by('date_stamp')
		data = []
		dates = list(set([h.date_stamp for h in histories]))
		dates.sort()
		for on_date in dates:
			data.append({
				'on_date':on_date,
				'ranks': [h.stock.symbol for h in histories.filter(date_stamp=on_date).order_by('-val_by_strategy')],
				})

		# simulate tradings
		assets = simulate_trading(self.request.user,data,histories,100000,self.request.user.myuserprofile.per_trade_total)

		# render HTML
		asset_dates = assets.keys()
		asset_dates.sort()
		asset_vals = [float(assets[d]) for d in asset_dates]
		content = loader.get_template(self.template_name)
		html= content.render(RequestContext(self.request,
			{'form':form,
			'data':data, 
			'start':data[0]['on_date'],
			'end':data[-1]['on_date'],
			'asset_dates':[a.isoformat() for a in asset_dates],
			'asset_vals':asset_vals}))
		# return super(MyStockStrategy2List, self).form_valid(form)
		return HttpResponse(html)
