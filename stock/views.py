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
from django.db.models import Count, Max, Min, Avg

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.vary import vary_on_headers
# protect the view with require_POST decorator
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q, F
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
import re
import os
import os.path
import shutil
import subprocess
import testtools
import sys
import random
import codecs
import unittest
import time
import tempfile
import csv
import hashlib
from datetime import datetime as dt
import simplejson as json
from itertools import groupby
import urllib
import lxml.html
from numpy import mean, std
import pickle
import cPickle
from utility import MyUtility, JSONEncoder

from stock.forms import *
from stock.models import *
from stock.simulations import MySimulationAlpha, MySimulationJK
from stock.tasks import MyStockBacktestingSimulation

###################################################
#
#   Common utilities
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
#   Static views
#
###################################################


class HomeView (TemplateView):
    """Home landing page.
    """
    template_name = 'intern/common/home_with_login_modal.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        user_auth_form = AuthenticationForm()
        user_registration_form = UserCreationForm()

        context['registration_form'] = user_registration_form
        context['auth_form'] = user_auth_form
        return context

###################################################
#
#   User views
#
###################################################


class LoginView(FormView):
    """Login page
    """
    template_name = 'registration/login.html'
    success_url = reverse_lazy('simulation_exec')
    form_class = AuthenticationForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None and user.is_active:
            login(self.request, user)
            return super(LoginView, self).form_valid(form)
        else:
            return self.form_invalid(form)


class LogoutView(TemplateView):
    """Logout page
    """
    template_name = 'registration/logged_out.html'

    def get(self, request):
        logout(request)
    # Redirect to a success page.
        # messages.add_message(request, messages.INFO, 'Thank you for using our service. Hope to see you soon!')
        return HttpResponseRedirect(reverse_lazy('home'))


class UserRegisterView(FormView):
    """User registration page
    """
    template_name = 'registration/register_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user_name = form.cleaned_data['username']
        password = form.cleaned_data['password2']
        if len(User.objects.filter(username=user_name)) > 0:
            return self.form_invalid(form)
        else:
            user = User.objects.create_user(user_name, '', password)
            user.save()

            return super(UserRegisterView, self).form_valid(form)

###################################################
#
#   MyApplication views
#
###################################################


class UserProfileView(TemplateView):
    template_name = 'stock/user/profile.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            user_profile, created = MyUserProfile.objects.get_or_create(
                owner=self.request.user)
        return context

    def post(self, request):
        pe_threshold = request.POST['pe'].strip()
        per_trade_total = request.POST['per_trade_total'].strip()
        exit_pcnt = request.POST['exit_pcnt'].strip()

        # get user property obj
        user_profile, created = MyUserProfile.objects.get_or_create(
            owner=request.user)
        user_profile.pe_threshold = pe_threshold
        try:
            user_profile.per_trade_total = float(per_trade_total)
        except:
            pass  # no change
        try:
            user_profile.exit_percent = int(exit_pcnt)
        except:
            pass
        user_profile.save()

        # refresh current page, whatever it is.
        return HttpResponseRedirect(request.META['HTTP_REFERER'])


class MyStockListFilter (FilterSet):

    class Meta:
        model = MyStock
        fields = {
            'company_name': ['contains'],
            'symbol': ['contains'],
            'is_in_play': ['exact'],
            # 'sponsor__is_sas_paying_student_fees':['exact'],
            # 'sponsor__is_to_return_balance':['exact']
        }


class MyStockList (FilterView):
    template_name = 'stock/stock/list.html'
    paginate_by = 500

    def get_filterset_class(self):
        return MyStockListFilter

class MyStockDetail(DetailView):
    model = MyStock
    template_name = 'stock/stock/detail.html'
    
    def get_context_data(self, **kwargs):
        context = super(MyStockDetail, self).get_context_data(**kwargs)
        on_dates = list(MyStockHistorical.objects.filter(stock=self.object).values_list('date_stamp', flat=True).order_by('date_stamp'))
        context['on_dates'] = [d.strftime('%Y-%m-%d') for d in on_dates]
        context['start'] = start = on_dates[0]
        context['end'] = end = on_dates[-1]
        context['open_prices'] = [float(x) for x in MyStockHistorical.objects.filter(stock=self.object).values_list('open_price', flat=True).order_by('date_stamp')]
        context['adj_close_prices'] = [float(x) for x in MyStockHistorical.objects.filter(stock=self.object).values_list('adj_close', flat=True).order_by('date_stamp')]


        # Pull index data for comparison
        if self.object.is_china_stock:
            # if viewing a China data, we pull China SP500 index
            index_symbol = '000001'
        elif self.object.is_sp500:
            # if viewing SP500 data, we pull SP500 index GSPC
            index_symbol = 'GSPC'
        context['index_close_prices'] = [float(x) for x in MyStockHistorical.objects.filter(stock__symbol=index_symbol,date_stamp__range=[start,end]).values_list('adj_close', flat=True).order_by('date_stamp')]
        return context

from tasks import stock_monitor_yahoo_consumer, stock_monitor_yahoo_consumer2


@class_view_decorator(login_required)
class MyStockUpdate(TemplateView):
    """Update S&P500 using Yahoo source.

    Add a background task to queue to process updates from Yahoo sources.
    """
    template_name = ''

    def post(self, request):
        step = 100
        total = 500
        symbols = MyStock.objects.filter(
            is_sp500=True).values_list('symbol', flat=True)
        for i in xrange(total / step):
            stock_monitor_yahoo_consumer.delay(
                ','.join(symbols[i * step:(i * step + step)]))
            stock_monitor_yahoo_consumer2.delay(
                ','.join(symbols[i * step:(i * step + step)]))

        return HttpResponse(json.dumps({'status': 'ok'}),
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
        context['up_up'] = MyStock.objects.filter(
            prev_change__gt=0, day_change__gt=0)
        context['down_up'] = MyStock.objects.filter(
            prev_change__lt=0, day_change__gt=0)
        context['up_down'] = MyStock.objects.filter(
            prev_change__gt=0, day_change__lt=0)
        context['down_down'] = MyStock.objects.filter(
            prev_change__lt=0, day_change__lt=0)
        return context


@class_view_decorator(login_required)
class MyStockTrendGain(TemplateView):
    template_name = 'stock/stock/trend_gain.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['direction'] = 'Gain'
        context['object_list'] = MyStock.objects.filter(
            prev_open__lt=F('last'))
        return context


@class_view_decorator(login_required)
class MyStockTrendLoss(TemplateView):
    template_name = 'stock/stock/trend_gain.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['direction'] = 'Loss'
        context['object_list'] = MyStock.objects.filter(
            prev_open__gt=F('last'))
        return context


@class_view_decorator(login_required)
class MyStockTrendConsistentGain(TemplateView):
    template_name = 'stock/stock/trend_gain.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['direction'] = 'Consistent gain'
        context['object_list'] = filter(
            lambda x: x.trend_is_consistent_gain, MyStock.objects.filter(prev_open__lt=F('last')))

        return context


@class_view_decorator(login_required)
class MyStockTrendConsistentLoss(TemplateView):
    template_name = 'stock/stock/trend_gain.html'

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        context['direction'] = 'Consistent loss'
        context['object_list'] = filter(
            lambda x: x.trend_is_consistent_loss, MyStock.objects.filter(prev_open__gt=F('last')))

        return context


@class_view_decorator(login_required)
class MyStockPosition(TemplateView):
    """View user's current open positions.
    """
    template_name = 'stock/stock/position.html'

    def post(self, request):
        stock = MyStock.objects.get(id=int(self.request.POST['obj_id']))
        pos_open = MyPosition.objects.filter(
            stock=stock, user=self.request.user, is_open=True)

        content = loader.get_template(self.template_name)
        html = content.render(
            Context({'pos_open': pos_open, 'obj_id': stock.id}))

        return HttpResponse(json.dumps({'html': html}),
                            content_type='application/javascript')


@class_view_decorator(login_required)
class MyStockTransaction(TemplateView):
    """Ajax view.

    This handles transactions of either buying or selling a particular position
    that requesting user currently has on his portfolio.
    """
    template_name = ''

    def post(self, request):
        stock = MyStock.objects.get(id=int(self.request.POST['obj_id']))
        transaction_type = self.request.POST['type']

        # get user property obj
        user_profile, created = MyUserProfile.objects.get_or_create(
            owner=request.user)

        # establish a new position
        if transaction_type == 'bid':  # buy 1
            vol = int(user_profile.per_trade_total / stock.last)
            pos = MyPosition(stock=stock, position=stock.last,
                             vol=vol, user=request.user)
            user_profile.cash -= pos.vol * pos.position

            user_profile.save()
            pos.save()

        elif transaction_type == 'ask':  # sell 1, FIFO
            pos = MyPosition.objects.filter(
                user=request.user, stock=stock, is_open=True).order_by('created')[0]
            pos.is_open = False
            pos.close_position = stock.last
            user_profile.cash += pos.vol * pos.close_position

            user_profile.save()
            pos.save()

        elif transaction_type == 'close':  # close positions
            for pos in MyPosition.objects.filter(user=request.user, stock=stock, is_open=True):
                pos.is_open = False
                pos.close_position = stock.last
                user_profile.cash += pos.vol * pos.close_position
                pos.save()

        # update records
        user_profile.save()

        return HttpResponse(json.dumps({'status': 'ok'}),
                            content_type='application/javascript')

from statistics import mean


@class_view_decorator(login_required)
class UserPositionList(ListView):
    template_name = 'stock/stock/position_list.html'

    def get_queryset(self):
        data = []
        stocks = MyPosition.objects.filter(
            user=self.request.user, is_open=True).values_list('stock', flat=True)
        for s in stocks:
            tmp = {'id': s, 'stock': MyStock.objects.get(id=s)}
            tmp['potential_gain'] = sum([a.potential_gain for a in MyPosition.objects.filter(
                user=self.request.user, is_open=True, stock=s)])
            tmp['life'] = mean([a.elapse_in_days for a in MyPosition.objects.filter(
                user=self.request.user, is_open=True, stock=s)])
            tmp['avg_cost'] = sum([a.total for a in MyPosition.objects.filter(user=self.request.user, is_open=True, stock=s)]) / \
                sum([a.vol for a in MyPosition.objects.filter(
                    user=self.request.user, is_open=True, stock=s)])
            data.append(tmp)
        return data


@class_view_decorator(login_required)
class MyStockCandidateList(ListView):
    template_name = 'stock/stock/trend_gain.html'

    def get_context_data(self, **kwargs):
        context = super(ListView, self).get_context_data(**kwargs)
        context['direction'] = 'Candidate'
        return context

    def get_queryset(self):
        stocks = MyStock.objects.all()
        return filter(lambda x: x.trend_is_consistent_loss and  # has been on down curve
                      # 2-day drop greater than 4%
                      (x.oneday_change < -2 or x.twoday_change < -4) and
                      x.fib_weekly_score_pcnt > 0 and  # weekly trending up
                      x.fib_daily_score_pcnt > 0 and  # daily trending up
                      # weekly trending up > drops
                      x.fib_weekly_score_pcnt + float(x.oneday_change) > 0 and
                      x.fib_weekly_score_pcnt + float(x.twoday_change) > 0 and
                      # daily trending up > drops
                      x.fib_daily_score_pcnt + float(x.oneday_change) > 0 and
                      x.fib_daily_score_pcnt + float(x.twoday_change) > 0,
                      stocks)

from nltk import FreqDist


@class_view_decorator(login_required)
class MyStockStrategy1Detail(TemplateView):
    model = MyStockHistorical
    template_name = 'stock/backtesting/s1_detail.html'

    def occurrences(self, haystack, needle):
        """Count occurences of a substring within a string.

        This is a helper function to count the number of occurance
        of a pattern (substring) within a string.

        Args:
                :haystack: a string or list. The long string we are to search for a pattern.
                :needle: a string or list. the pattern we are searching.

        Returns:
                :int: number of occurance
        """
        return sum(haystack[i:i + len(needle)] == needle for i in xrange(len(haystack) - len(needle) + 1))

    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        stock = MyStock.objects.get(symbol__iexact=self.kwargs['symbol'])
        context['stock'] = stock

        histories = MyStockHistorical.objects.filter(
            stock=stock).order_by('date_stamp')
        histories = tmp = ''.join([h.flag_by_strategy for h in histories])
        tmp = re.sub('[U]+', 'U', tmp)
        tmp = re.sub('[G]+', 'G', tmp)
        tmp = re.sub('[L]+', 'L', tmp)
        context['flag_by_strategy'] = histories

        # probabilities
        total_sample = len(tmp) - 5 + 1
        context['prob_ggg'] = self.occurrences(tmp, 'GUGUG')
        context['prob_ggl'] = self.occurrences(tmp, 'GUGUL')
        context['prob_glg'] = self.occurrences(tmp, 'GULUG')
        context['prob_gll'] = self.occurrences(tmp, 'GULUL')
        context['prob_lgg'] = self.occurrences(tmp, 'LUGUG')
        context['prob_lgl'] = self.occurrences(tmp, 'LUGUL')
        context['prob_llg'] = self.occurrences(tmp, 'LULUG')
        context['prob_lll'] = self.occurrences(tmp, 'LULUL')
        context['prob_conseq_u'] = FreqDist(
            [str(len(x)) for x in re.findall('[U]+', histories)]).most_common(10)
        context['prob_conseq_g'] = FreqDist(
            [str(len(x)) for x in re.findall('[G]+', histories)]).most_common(10)
        context['prob_conseq_l'] = FreqDist(
            [str(len(x)) for x in re.findall('[L]+', histories)]).most_common(10)
        context['ending_g_over_l'] = sum([context['prob_ggg'], context['prob_glg'], context['prob_lgg'], context[
                                         'prob_llg']]) * 1.0 / sum([context['prob_ggl'], context['prob_gll'], context['prob_lgl'], context['prob_lll']])

        context['peers'] = MyStock.objects.all(
        ).values_list('symbol', flat=True)
        return context

######################################################
#
#   Simulator views
#
#####################################################
from stock.tasks import backtesting_simulation_consumer


@class_view_decorator(login_required)
class MySimulationExec(FormView):
    template_name = 'stock/backtesting/simulation_exec.html'
    form_class = StrategyControlForm

    def form_valid(self, form):
        # persist simulation conditions
        condition, created = MySimulationCondition.objects.get_or_create(
            **form.cleaned_data)

        # run simulation for 1st time
        if not MyPosition.objects.filter(simulation=condition):
            # MySimulationCondition is not JSON serializable
            # so we use cPickle to pass object to background queue task
            backtesting_simulation_consumer.delay(cPickle.dumps(condition))
            return HttpResponseRedirect(reverse_lazy('simulation_result_list'))
        else:
            return HttpResponseRedirect(reverse_lazy('condition_detail', kwargs={'pk': condition.id}))

@class_view_decorator(login_required)
class MyStockHistoricalList(FormView):
    template_name = 'stock/stock/list_historicals.html'
    form_class = HistoricalListForm

    def form_valid(self, form):
        # control variables
        on_date = form.cleaned_data['on_date']

        # sample set
        data_source = form.cleaned_data['data_source']
        if data_source == '1':
            data_source = 'S&P 500'
            stocks = MyStock.objects.filter(
                is_sp500=True).values_list('id', flat=True)
        elif data_source == '2':
            data_source = 'CI sector'
            stocks = MyStock.objects.filter(
                symbol__startswith="CI00").values_list('id', flat=True)
        elif data_source == '3':
            data_source = 'WIND sector'
            stocks = MyStock.objects.filter(
                symbol__startswith="8821").values_list('id', flat=True)
        elif data_source == '4':
            data_source = 'China stock'
            stocks = MyStock.objects.filter(
                is_china_stock=True).values_list('id', flat=True)

        historicals = MyStockHistorical.objects.select_related().filter(
            stock__in=stocks, date_stamp=on_date)

        # render HTML
        return render(self.request, self.template_name, {
            'form': form,
            'data_source': data_source,
            'on_date': on_date,
            'historicals': historicals})


class MySimulationConditionDelete(DeleteView):
    model = MySimulationCondition
    template_name = 'stock/common/delete_form.html'
    success_url = reverse_lazy('simulation_result_list')

@class_view_decorator(login_required)
class MySimulationResultList(ListView):
    model = MySimulationCondition
    template_name = 'stock/backtesting/simulation_result_list.html'

    def get_queryset(self):
        return MySimulationCondition.objects.filter(
            strategy = 2,
        )

@class_view_decorator(login_required)
class MySimulationResultComp(TemplateView):
    template_name = 'stock/backtesting/simulation_result_comp.html'

    def post(self, request, *args, **kwargs):
        conditions = []
        for cond_id in self.request.POST.getlist('conditions'):
            condition = MySimulationCondition.objects.get(id=int(cond_id))
            conditions.append(condition)

        # Get all dates covered by simualtions
        all_dates = list(set(reduce(lambda x, y: x + y,
                                    [c.mysimulationresult.on_dates for c in conditions])))
        all_dates = sorted(all_dates)

        assets = []
        for cond in conditions:
            start_date = cond.mysimulationresult.on_dates[0]
            end_date = cond.mysimulationresult.on_dates[-1]

            # we are to padding 0s to front and back so two simulations
            # have the same start date and end date to compare their asset
            # values
            padding_start = all_dates.index(start_date)
            padding_end = len(all_dates) - \
                all_dates.index(end_date) - 1  # 0-index
            assets.append({'name': cond, 'values': [
                          0] * padding_start + cond.mysimulationresult.asset + [0] * padding_end})

        return render(request, self.template_name, {
            'object_list': conditions,
            'on_dates': [str(d) for d in all_dates],
            'start': all_dates[0],
            'end': all_dates[-1],
            'assets': assets})


@class_view_decorator(login_required)
class MySimulationConditionDetail(DetailView):
    template_name = 'stock/backtesting/simulation_result_detail.html'
    model = MySimulationCondition

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        cond = self.object
        snapshots = MySimulationSnapshot.objects.filter(simulation=cond).order_by('on_date')

        context['strategy'] = cond
        context['start'] = cond.start
        context['end'] = cond.end
        context['on_dates'] = [s.on_date.strftime('%Y-%m-%d') for s in snapshots]
        context['assets'] = [float(a) for a in MySimulationSnapshot.objects.filter(simulation=cond).values_list('asset', flat=True).order_by('on_date')]
        context['cashes'] = [float(a) for a in MySimulationSnapshot.objects.filter(simulation=cond).values_list('cash', flat=True).order_by('on_date')]
        context['equities'] = [float(a) for a in MySimulationSnapshot.objects.filter(simulation=cond).values_list('equity', flat=True).order_by('on_date')]
        context['snapshots'] = snapshots
        context['gain_from_holding'] = [float(x) for x in cond.gain_from_holding]
        context['gain_from_exit'] = [float(x) for x in cond.gain_from_exit]
        context['asset_gain_pcnt_t0'] = cond.asset_gain_pcnt_t0[1:]

        # Pull index data for comparison
        if self.object.data_source in [2, 3, 4, 5]:
            # if viewing a China data, we pull China SP500 index
            index_symbol = '000001'
        elif self.object.data_source == 1:
            # if viewing SP500 data, we pull SP500 index GSPC
            index_symbol = 'GSPC'

        # compute ndex cumulative return for selected time period
        index_historicals = MyStockHistorical.objects.filter(
            stock__symbol=index_symbol, date_stamp__in=context['on_dates']).values('adj_close').order_by('date_stamp')
        index_t0 = index_historicals[0]['adj_close']

        # index historicals normalized to its T0 value
        context['index_gain_pcnt'] = [float(index_historicals[x]['adj_close'] / index_t0) 
            for x in range(1, len(index_historicals))]
 
        # alpha return is the diff between measured asset returns and index returns
        # < 0: when portfolio is underforming index; >0: overperforming
        context['alpha_return'] = map(lambda x: x[0] - x[1], zip(context['asset_gain_pcnt_t0'], context['index_gain_pcnt']))

        return context
