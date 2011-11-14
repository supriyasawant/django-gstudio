"""Defaults urls for the Objectapp project"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    '',
    url(r'^tags/', include('objectapp.urls.tags',)),
    url(r'^feeds/', include('objectapp.urls.feeds')),
    url(r'^authors/', include('objectapp.urls.authors')),
    url(r'^objecttypes/', include('objectapp.urls.objecttypes')),
    url(r'^search/', include('objectapp.urls.search')),
    url(r'^sitemap/', include('objectapp.urls.sitemap')),
    url(r'^trackback/', include('objectapp.urls.trackback')),
    url(r'^discussions/', include('objectapp.urls.discussions')),
    url(r'^', include('objectapp.urls.quick_gbobject')),
    url(r'^', include('objectapp.urls.capabilities')),
    url(r'^', include('objectapp.urls.gbobjects')),
    )
