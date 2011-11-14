"""Urls for the Relationapp search"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('relationapp.views.search',
                       url(r'^$', 'relationtype_search', name='relationapp_relationtype_search'),
                       )
