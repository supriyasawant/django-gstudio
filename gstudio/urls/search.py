"""Urls for the Gstudio search"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('gstudio.views.search',
                       url(r'^$', 'nodetype_search', name='gstudio_nodetype_search'),
                       )
