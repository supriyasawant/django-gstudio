"""Urls for the Gstudio trackback"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('gstudio.views.trackback',
                       url(r'^(?P<object_id>\d+)/$', 'objecttype_trackback',
                           name='gstudio_objecttype_trackback'),
                       )
