"""Urls for the Objectapp tags"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('objectapp.views.tags',
                       url(r'^$', 'tag_list',
                           name='objectapp_tag_list'),
                       url(r'^(?P<tag>[^/]+(?u))/$', 'tag_detail',
                           name='objectapp_tag_detail'),
                       url(r'^(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$',
                           'tag_detail', name='objectapp_tag_detail_paginated'),
                       )
