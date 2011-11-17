"""Urls for the Objectapp gbobjects"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from objectapp.models import Gbobject
from objectapp.settings import PAGINATION
from objectapp.settings import ALLOW_EMPTY
from objectapp.settings import ALLOW_FUTURE

gbobject_conf_index = {'paginate_by': PAGINATION,
                    'template_name': 'objectapp/gbobject_archive.html'}

gbobject_conf = {'date_field': 'creation_date',
              'allow_empty': ALLOW_EMPTY,
              'allow_future': ALLOW_FUTURE,
              'month_format': '%m'}

gbobject_conf_year = gbobject_conf.copy()
gbobject_conf_year['make_object_list'] = True
del gbobject_conf_year['month_format']

gbobject_conf_detail = gbobject_conf.copy()
del gbobject_conf_detail['allow_empty']
gbobject_conf_detail['queryset'] = Gbobject.published.on_site()


urlpatterns = patterns(
    'objectapp.views.gbobjects',
    url(r'^$',
        'gbobject_index', gbobject_conf_index,
        name='objectapp_gbobject_archive_index'),
    url(r'^page/(?P<page>\d+)/$',
        'gbobject_index', gbobject_conf_index,
        name='objectapp_gbobject_archive_index_paginated'),
    url(r'^(?P<year>\d{4})/$',
        'gbobject_year', gbobject_conf_year,
        name='objectapp_gbobject_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        'gbobject_month', gbobject_conf,
        name='objectapp_gbobject_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        'gbobject_day', gbobject_conf,
        name='objectapp_gbobject_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        'gbobject_detail', gbobject_conf_detail,
        name='objectapp_gbobject_detail'),
    url(r'^(?P<object_id>\d+)/$',
        'gbobject_shortlink',
        name='objectapp_gbobject_shortlink'),
    )
