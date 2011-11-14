"""Urls for the Objectapp search"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('objectapp.views.search',
                       url(r'^$', 'gbobject_search', name='objectapp_gbobject_search'),
                       )
