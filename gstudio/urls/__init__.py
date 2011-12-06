"""Defaults urls for the Gstudio project"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    '',
    url(r'^tags/', include('gstudio.urls.tags',)),
    url(r'^feeds/', include('gstudio.urls.feeds')),
    url(r'^authors/', include('gstudio.urls.authors')),
    url(r'^metatypes/', include('gstudio.urls.metatypes')),
    url(r'^search/', include('gstudio.urls.search')),
    url(r'^sitemap/', include('gstudio.urls.sitemap')),
    url(r'^trackback/', include('gstudio.urls.trackback')),
    url(r'^discussions/', include('gstudio.urls.discussions')),
    url(r'^', include('gstudio.urls.quick_nodetype')),
    url(r'^', include('gstudio.urls.capabilities')),
    url(r'^', include('gstudio.urls.nodetypes')),
    )
