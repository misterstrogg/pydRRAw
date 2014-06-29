from django.conf.urls import patterns, include, url

from django.contrib import admin
import admin_tools
admin.autodiscover()

base_urlpatterns = patterns('',
#    url(r'^admin_tools/', include(admin_tools.urls)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^pydrraw/', include('pydrraw.urls', namespace="pydrraw")),
)
urlpatterns = patterns('',
    url(r'', include(base_urlpatterns)),
    url(r'^pysite/', include(base_urlpatterns)),
)
