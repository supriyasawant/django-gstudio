"""Test urls for the attributeapp project"""
from functools import wraps

from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

from attributeapp.views.tags import tag_detail
from attributeapp.views.authors import author_detail
from attributeapp.views.attributes import attribute_detail
from attributeapp.tests.urls import urlpatterns as test_urlpatterns


def call_with_template_and_extra_context(
    view, template_name='attributeapp/attributetype_list.html',
    extra_context={'extra': 'context'}):

    @wraps(view)
    def wrapper(*args, **kwargs):
        return view(template_name=template_name,
                    extra_context=extra_context,
                    *args, **kwargs)

    return wrapper

custom_tag_detail = call_with_template_and_extra_context(tag_detail)
custom_author_detail = call_with_template_and_extra_context(author_detail)
custom_attribute_detail = call_with_template_and_extra_context(attribute_detail)


urlpatterns = patterns(
    '',
    url(r'^authors/(?P<username>[.+-@\w]+)/$',
        custom_author_detail, name='attributeapp_author_detail'),
    url(r'^authors/(?P<username>[.+-@\w]+)/page/(?P<page>\d+)/$',
        custom_author_detail, name='attributeapp_author_detail_paginated'),
    url(r'^attributes/(?P<path>[-\/\w]+)/page/(?P<page>\d+)/$',
        custom_attribute_detail, name='attributeapp_attribute_detail_paginated'),
    url(r'^attributes/(?P<path>[-\/\w]+)/$',
        custom_attribute_detail, name='attributeapp_attribute_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/$',
        custom_tag_detail, name='attributeapp_tag_detail'),
    url(r'^tags/(?P<tag>[- \w]+)/page/(?P<page>\d+)/$',
        custom_tag_detail, name='attributeapp_tag_detail_paginated'),
    ) + test_urlpatterns
