"""Urls for the Gstudio metatypes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from gstudio.models import Metatype

metatype_conf = {'queryset': Metatype.tree.all()}

urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^$', 'object_list',
                           metatype_conf, 'gstudio_metatype_list'),
                       )

urlpatterns += patterns('gstudio.views.metatypes',
                        url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            'metatype_detail',
                            name='gstudio_metatype_detail_paginated'),
                        url(r'^(?P<path>[-\/\w]+)/$', 'metatype_detail',
                            name='gstudio_metatype_detail'),
                        )
