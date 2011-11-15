"""Urls for the Attributeapp attributes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from attributeapp.models import Attribute

attribute_conf = {'queryset': Attribute.tree.all()}

urlpatterns = patterns('django.views.generic.list_detail',
                       url(r'^$', 'object_list',
                           attribute_conf, 'attributeapp_attribute_list'),
                       )

urlpatterns += patterns('attributeapp.views.attributes',
                        url(r'^(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
                            'attribute_detail',
                            name='attributeapp_attribute_detail_paginated'),
                        url(r'^(?P<path>[-\/\w]+)/$', 'attribute_detail',
                            name='attributeapp_attribute_detail'),
                        )
