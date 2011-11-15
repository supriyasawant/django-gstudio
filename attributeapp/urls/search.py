"""Urls for the Attributeapp search"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('attributeapp.views.search',
                       url(r'^$', 'attributetype_search', name='attributeapp_attributetype_search'),
                       )
