"""Urls for the Objectapp objecttypes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from objectapp.models import Objecttype

Objecttype_conf = {'queryset': Objecttype.tree.all()}

urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^$', 'object_list',
                           Objecttype_conf, 'objectapp_Objecttype_list'),
                       )

urlpatterns += patterns('objectapp.views.objecttypes',
                        url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            'Objecttype_detail',
                            name='objectapp_Objecttype_detail_paginated'),
                        url(r'^(?P<path>[-\/\w]+)/$', 'Objecttype_detail',
                            name='objectapp_Objecttype_detail'),
                        )
