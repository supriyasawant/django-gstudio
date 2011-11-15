"""Urls for the Attributeapp authors"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns


urlpatterns = patterns('attributeapp.views.authors',
                       url(r'^$', 'author_list',
                           name='attributeapp_author_list'),
                       url(r'^(?P<username>[.+-@\w]+)/$', 'author_detail',
                           name='attributeapp_author_detail'),
                       url(r'^(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
                           'author_detail',
                           name='attributeapp_author_detail_paginated'),
                       )
