from django.conf.urls import patterns, include, url
from grappelli.urls import urlpatterns as grappelli_urls
from django.contrib import admin
import admin_tools
admin.autodiscover()

base_urlpatterns = patterns('',
#    url(r'^admin_tools/', include(admin_tools.urls)),
    url(r'^grappelli/', include(grappelli_urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pydrraw/', include('pydrraw.urls', namespace="pydrraw")),
)
urlpatterns = patterns('',
    url(r'', include(base_urlpatterns)),
    url(r'^pysite/', include(base_urlpatterns)),
)
