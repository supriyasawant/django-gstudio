"""Urls for the Relationapp relationtypes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from relationapp.models import Relationtype
from relationapp.settings import PAGINATION
from relationapp.settings import ALLOW_EMPTY
from relationapp.settings import ALLOW_FUTURE

relationtype_conf_index = {'paginate_by': PAGINATION,
                    'template_name': 'relationapp/relationtype_archive.html'}

relationtype_conf = {'date_field': 'creation_date',
                   'allow_empty': ALLOW_EMPTY,
                   'allow_future': ALLOW_FUTURE,
                   'month_format': '%m',
                   'queryset': Relationtype.tree.all()}

relation_conf = {}

relationtype_conf_year = relationtype_conf.copy()
relationtype_conf_year['make_object_list'] = True
del relationtype_conf_year['month_format']

relationtype_conf_detail = relationtype_conf.copy()
del relationtype_conf_detail['allow_empty']
relationtype_conf_detail['queryset'] = Relationtype.published.on_site()


urlpatterns = patterns(
    'relationapp.views.relationtypes',
    url(r'^$',
        'relationtype_index', relationtype_conf_index,
        name='relationapp_relationtype_archive_index'),
    url(r'^page/(?P<page>\d+)/$',
        'relationtype_index', relationtype_conf_index,
        name='relationapp_relationtype_archive_index_paginated'),
    url(r'^(?P<year>\d{4})/$',
        'relationtype_year', relationtype_conf_year,
        name='relationapp_relationtype_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        'relationtype_month', relationtype_conf,
        name='relationapp_relationtype_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        'relationtype_day', relationtype_conf,
        name='relationapp_relationtype_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        'relationtype_detail', relationtype_conf_detail,
        name='relationapp_relationtype_detail'),
    url(r'^(?P<object_id>\d+)/$',
        'relationtype_shortlink',
        name='relationapp_relationtype_shortlink'),
    )
