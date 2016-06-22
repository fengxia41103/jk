from django.conf.urls import patterns, url
from django.conf.urls import url
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import UserCreationForm
import django.contrib.auth.views as AuthViews
from django.views.decorators.csrf import ensure_csrf_cookie
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import cache_page
from stock import views

urlpatterns = patterns(
    '',
    # url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^$', views.LoginView.as_view(), name='home'),
    url(r'login/$', views.LoginView.as_view(), name='login'),
    url(r'logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^register/$', views.UserRegisterView.as_view(),
        name='user_register'),

    # user related
    url(r'^user/profile/$', views.UserProfileView.as_view(),
        name='user_profile'),
    url(r'^user/position/$', views.UserPositionList.as_view(),
        name='user_position_list'),

    url(r'^stock/$', views.MyStockList.as_view(), name='stock_list'),
    url(r'^stock/(?P<pk>\d+)/$', views.MyStockDetail.as_view(), name='stock_detail'),
    url(r'^stock/update/$', views.MyStockUpdate.as_view(),
        name='stock_update'),
    url(r'^historicals/$', views.MyStockHistoricalList.as_view(),
        name='stock_historicals_list'),


    # heat
    url(r'^heat/prev/change/$',
        views.MyStockHeatPrevChange.as_view(), name='heat_prev_change'),
    url(r'^heat/vol/over/float/$',
        views.MyStockHeatVolOverFloat.as_view(), name='heat_vol_over_float'),
    url(r'^heat/spread/$', views.MyStockHeatSpread.as_view(),
        name='heat_spread'),
    url(r'^heat/day/change/$',
        views.MyStockHeatDayChange.as_view(), name='heat_day_change'),

    # trend
    url(r'^trend/2day/$', views.MyStockTrendTransition.as_view(),
        name='trend_2day_transition'),
    url(r'^trend/2day/gain/$',
        views.MyStockTrendGain.as_view(), name='trend_2day_gain'),
    url(r'^trend/2day/loss/$',
        views.MyStockTrendLoss.as_view(), name='trend_2day_loss'),
    url(r'^trend/consistent/gain/$',
        views.MyStockTrendConsistentGain.as_view(), name='trend_consistent_gain'),
    url(r'^trend/consistent/loss/$',
        views.MyStockTrendConsistentLoss.as_view(), name='trend_consistent_loss'),

    # transaction
    url(r'^transaction/$', views.MyStockTransaction.as_view(),
        name='transaction'),
    url(r'^position/$', views.MyStockPosition.as_view(), name='position'),
    url(r'^candidate/$', views.MyStockCandidateList.as_view(),
        name='candidate_list'),

    # backtesting

    url(r'^condition/delete/(?P<pk>\d+)/$',
        views.MySimulationConditionDelete.as_view(), name='condition_delete'),
    url(r'^condition/detail/(?P<pk>\d+)/$',
        views.MySimulationConditionDetail.as_view(), name='condition_detail'),

    url(r'^backtesting/s1/(?P<symbol>\w+)/$',
        views.MyStockStrategy1Detail.as_view(), name='backtesting_1'),
    url(r'^backtesting/simulation/$',
        views.MySimulationExec.as_view(), name='simulation_exec'),
    url(r'^backtesting/result/$', views.MySimulationResultList.as_view(),
        name='simulation_result_list'),
    url(r'^backtesting/result/comp/$',
        views.MySimulationResultComp.as_view(), name='simulation_result_comp'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
