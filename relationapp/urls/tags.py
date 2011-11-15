"""Urls for the Relationapp tags"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('relationapp.views.tags',
                       url(r'^$', 'tag_list',
                           name='relationapp_tag_list'),
                       url(r'^(?P<tag>[^/]+(?u))/$', 'tag_detail',
                           name='relationapp_tag_detail'),
                       url(r'^(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$',
                           'tag_detail', name='relationapp_tag_detail_paginated'),
                       )
