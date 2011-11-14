"""Urls for the Objectapp authors"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns


urlpatterns = patterns('objectapp.views.authors',
                       url(r'^$', 'author_list',
                           name='objectapp_author_list'),
                       url(r'^(?P<username>[.+-@\w]+)/$', 'author_detail',
                           name='objectapp_author_detail'),
                       url(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
                           'author_detail',
                           name='objectapp_author_detail_paginated'),
                       )
