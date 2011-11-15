"""Urls for the Objectapp objecttypes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from objectapp.models import Objecttype

objecttype_conf = {'queryset': Objecttype.tree.all()}

urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^$', 'object_list',
                           objecttype_conf, 'objectapp_objecttype_list'),
                       )

urlpatterns += patterns('objectapp.views.objecttypes',
                        url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            'objecttype_detail',
                            name='objectapp_objecttype_detail_paginated'),
                        url(r'^(?P<path>[-\/\w]+)/$', 'objecttype_detail',
                            name='objectapp_objecttype_detail'),
                        )
