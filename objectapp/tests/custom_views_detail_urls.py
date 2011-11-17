"""Test urls for the objectapp project"""
from functools import wraps

from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from objectapp.views.tags import tag_detail
from objectapp.views.authors import author_detail
from objectapp.views.objecttypes import Objecttype_detail
from objectapp.tests.urls import urlpatterns as test_urlpatterns


def call_with_template_and_extra_context(
    view, template_name='objectapp/gbobject_list.html',
    extra_context={'extra': 'context'}):

    @wraps(view)
    def wrapper(*args, **kwargs):
        return view(template_name=template_name,
                    extra_context=extra_context,
                    *args, **kwargs)

    return wrapper

custom_tag_detail = call_with_template_and_extra_context(tag_detail)
custom_author_detail = call_with_template_and_extra_context(author_detail)
custom_Objecttype_detail = call_with_template_and_extra_context(Objecttype_detail)


urlpatterns = patterns(
    '',
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        custom_author_detail, name='objectapp_author_detail'),
    url(r'^authors/(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
        custom_author_detail, name='objectapp_author_detail_paginated'),
    url(r'^objecttypes/(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
        custom_Objecttype_detail, name='objectapp_Objecttype_detail_paginated'),
    url(r'^objecttypes/(?P<path>[-\/\w]+)/$',
        custom_Objecttype_detail, name='objectapp_Objecttype_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/$',
        custom_tag_detail, name='objectapp_tag_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
        custom_tag_detail, name='objectapp_tag_detail_paginated'),
    ) + test_urlpatterns
