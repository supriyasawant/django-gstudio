"""Urls for the Gstudio objecttypes"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from gstudio.models import Objecttype
from gstudio.settings import PAGINATION
from gstudio.settings import ALLOW_EMPTY
from gstudio.settings import ALLOW_FUTURE

objecttype_conf_index = {'paginate_by': PAGINATION,
                    'template_name': 'gstudio/objecttype_archive.html'}

objecttype_conf = {'date_field': 'creation_date',
              'allow_empty': ALLOW_EMPTY,
              'allow_future': ALLOW_FUTURE,
              'month_format': '%m'}

objecttype_conf_year = objecttype_conf.copy()
objecttype_conf_year['make_object_list'] = True
del objecttype_conf_year['month_format']

objecttype_conf_detail = objecttype_conf.copy()
del objecttype_conf_detail['allow_empty']
objecttype_conf_detail['queryset'] = Objecttype.published.on_site()


urlpatterns = patterns(
    'gstudio.views.objecttypes',
    url(r'^$',
        'objecttype_index', objecttype_conf_index,
        name='gstudio_objecttype_archive_index'),
    url(r'^page/(?P<page>\d+)/$',
        'objecttype_index', objecttype_conf_index,
        name='gstudio_objecttype_archive_index_paginated'),
    url(r'^(?P<year>\d{4})/$',
        'objecttype_year', objecttype_conf_year,
        name='gstudio_objecttype_archive_year'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$',
        'objecttype_month', objecttype_conf,
        name='gstudio_objecttype_archive_month'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$',
        'objecttype_day', objecttype_conf,
        name='gstudio_objecttype_archive_day'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$',
        'objecttype_detail', objecttype_conf_detail,
        name='gstudio_objecttype_detail'),
    url(r'^(?P<object_id>\d+)/$',
        'objecttype_shortlink',
        name='gstudio_objecttype_shortlink'),
    )
