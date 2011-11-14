"""Defaults urls for the Relationapp project"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    '',
    url(r'^tags/', include('relationapp.urls.tags',)),
    url(r'^feeds/', include('relationapp.urls.feeds')),
    url(r'^authors/', include('relationapp.urls.authors')),
    url(r'^relations/', include('relationapp.urls.relations')),
    url(r'^search/', include('relationapp.urls.search')),
    url(r'^sitemap/', include('relationapp.urls.sitemap')),
    url(r'^trackback/', include('relationapp.urls.trackback')),
    url(r'^discussions/', include('relationapp.urls.discussions')),
    url(r'^', include('relationapp.urls.quick_relationtype')),
    url(r'^', include('relationapp.urls.capabilities')),
    url(r'^', include('relationapp.urls.relationtypes')),
    )
