"""Urls for the Gstudio search"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('gstudio.views.search',
                       url(r'^$', 'objecttype_search', name='gstudio_objecttype_search'),
                       )
