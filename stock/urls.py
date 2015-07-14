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
		url(r'^stock/heat/$', views.MyStockListHeat.as_view(), name='stock_list_heat'),		
		url(r'^stock/update/$', views.MyStockUpdate.as_view(), name='stock_update'),
				
	)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
