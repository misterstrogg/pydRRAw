from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from pydrraw import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pydrraw.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    #url(r'^admin/', include(admin.site.urls)),

    url(r'^list/(?P<rrdpathname>(.*))/$', 'pydrraw.views.list'),
    url(r'^info/(?P<rrdpathname>(.*?))/(?P<rrd>(.*))/$', 'pydrraw.views.infoview', name='headerinfo'),
    url(r'^raw/(?P<rrdpathname>(.*?))/(?P<rrd>(.*))/$', 'pydrraw.views.raw', name='rawview'),
    url(r'^data/(?P<rrdpathname>(.*?))/(?P<rrd>(.*))/(?P<ds>(.*?))/(?P<rra>(.*?))/$', 'pydrraw.views.data', name='dataview'),
    url(r'^graphdetail(?P<pk>\d+)/$', views.GraphDetailView.as_view(), name='graphdetail'),
    url(r'^drawgraph/(?P<graphid>(.*))/$', 'pydrraw.views.drawgraph', name='drawgraph'),
    url(r'^editgraph/(?P<graphid>(.*))/$', 'pydrraw.views.editgraph', name='editgraph'),
    url(r'^editgraph/$', 'pydrraw.views.editgraph', name='editgraph'),
    url(r'^dash/(?P<dashid>(.*))/$', 'pydrraw.views.dash', name='dash'),
    url(r'^drawsimplegraph/(?P<rrdpathname>(.*?))/(?P<rrd>(.+))/(?P<ds>(.*?))/(?P<rra>(.*?))/$', 'pydrraw.views.drawsimplegraph', name='drawsimplegraph'),
    #url(r'^fresh/(?P<rrd>(.*))/(?P<ds>(.*))/(?P<rra>(.*))/$', 'pydrraw.views.fresh'),
    #url(r'^graph/(?P<rrdpathname>(.*?))/(?P<rrd>(.+))/$', 'pydrraw.views.graph', name='graphview'),
    url(r'^(?P<rrdpathname>(.*))/$', 'pydrraw.views.list'),
    url(r'^$', 'pydrraw.views.list', {'rrdpathname':'all'}),
)
