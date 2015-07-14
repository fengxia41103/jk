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
		url(r'login/$', views.LoginView.as_view(),name='login'),
		url(r'logout/$', views.LogoutView.as_view(), name='logout'),
		url(r'^register/$', views.UserRegisterView.as_view(), name='user_register'),

		# user related
		url(r'^user/profile/$', views.UserProfileView.as_view(), name='user_profile'),

		url(r'^stock/$', views.MyStockList.as_view(), name='stock_list'),
		url(r'^stock/update/$', views.MyStockUpdate.as_view(), name='stock_update'),
		url(r'^heat/prev/change/$', views.MyStockHeatPrevChange.as_view(), name='heat_prev_change'),		
		url(r'^heat/vol/over/float/$', views.MyStockHeatVolOverFloat.as_view(), name='heat_vol_over_float'),		
		url(r'^heat/spread/$', views.MyStockHeatSpread.as_view(), name='heat_spread'),		
		url(r'^heat/day/change/$', views.MyStockHeatDayChange.as_view(), name='heat_day_change'),		
				
	)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
