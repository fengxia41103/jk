from django.conf.urls import patterns, include, url
from django.contrib import admin
import settings


######################################################
#
#   RESTful API endpoints
#
#####################################################
from rest_framework import routers
from stock.models import *

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'stock', MyStockViewSet)


urlpatterns = patterns('',
                       url(r'^admin/', include(admin.site.urls)),
                       url('', include(
                           'social.apps.django_app.urls', namespace='social')),
                       url('', include('django.contrib.auth.urls', namespace='auth')),

                       # django-restframework
                       url(r'^api/', include(router.urls)),
                       url(r'^api-auth/', include('rest_framework.urls',
                                                  namespace='rest_framework')),

                       # application specific
                       url(r'^jk/', include('stock.urls')),
                       )

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )

    urlpatterns += patterns('django.contrib.staticfiles.views',
                            url(r'^static/(?P<path>.*)$', 'serve'),
                            )
