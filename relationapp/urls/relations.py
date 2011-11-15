"""Urls for the Relationapp relations"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from relationapp.models import Relation

relation_conf = {'queryset': Relation.tree.all()}

urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^$', 'object_list',
                           relation_conf, 'relationapp_relation_list'),
                       )

urlpatterns += patterns('relationapp.views.relations',
                        url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            'relation_detail',
                            name='relationapp_relation_detail_paginated'),
                        url(r'^(?P<path>[-\/\w]+)/$', 'relation_detail',
                            name='relationapp_relation_detail'),
                        )
