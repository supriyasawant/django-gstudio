"""Urls for the Gstudio authors"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns


urlpatterns = patterns('gstudio.views.authors',
                       url(r'^$', 'author_list',
                           name='gstudio_author_list'),
                       url(r'^(?P<username>[.+-@\w]+)/$', 'author_detail',
                           name='gstudio_author_detail'),
                       url(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
                           'author_detail',
                           name='gstudio_author_detail_paginated'),
                       )
