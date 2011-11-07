"""Urls for the Gstudio tags"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('gstudio.views.tags',
                       url(r'^$', 'tag_list',
                           name='gstudio_tag_list'),
                       url(r'^(?P<tag>[^/]+(?u))/$', 'tag_detail',
                           name='gstudio_tag_detail'),
                       url(r'^(?P<tag>[^/]+(?u))/page/(?P<page>\d+)/$',
                           'tag_detail', name='gstudio_tag_detail_paginated'),
                       )
