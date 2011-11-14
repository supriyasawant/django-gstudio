"""Urls for the Attributeapp attributetypes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from attributeapp.models import Attributetype
from attributeapp.settings import PAGINATION
from attributeapp.settings import ALLOW_EMPTY
from attributeapp.settings import ALLOW_FUTURE

attributetype_conf_index = {'paginate_by': PAGINATION,
                    'template_name': 'attributeapp/attributetype_archive.html'}

attributetype_conf = {'date_field': 'creation_date',
                   'allow_empty': ALLOW_EMPTY,
                   'allow_future': ALLOW_FUTURE,
                   'month_format': '%m',
                   'queryset': Attributetype.tree.all()}

attribute_conf = {}

attributetype_conf_year = attributetype_conf.copy()
attributetype_conf_year['make_object_list'] = True
del attributetype_conf_year['month_format']

attributetype_conf_detail = attributetype_conf.copy()
del attributetype_conf_detail['allow_empty']
attributetype_conf_detail['queryset'] = Attributetype.published.on_site()


urlpatterns = patterns(
    'attributeapp.views.attributetypes',
    url(r'^$',
        'attributetype_index', attributetype_conf_index,
        name='attributeapp_attributetype_archive_index'),
    url(r'^page/(?P<page>\d+)/$',
        'attributetype_index', attributetype_conf_index,
        name='attributeapp_attributetype_archive_index_paginated'),
    url(r'^(?P<year>\d{4})/$',
        'attributetype_year', attributetype_conf_year,
        name='attributeapp_attributetype_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        'attributetype_month', attributetype_conf,
        name='attributeapp_attributetype_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        'attributetype_day', attributetype_conf,
        name='attributeapp_attributetype_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        'attributetype_detail', attributetype_conf_detail,
        name='attributeapp_attributetype_detail'),
    url(r'^(?P<object_id>\d+)/$',
        'attributetype_shortlink',
        name='attributeapp_attributetype_shortlink'),
    )
