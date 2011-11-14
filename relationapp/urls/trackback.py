"""Urls for the Relationapp trackback"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('relationapp.views.trackback',
                       url(r'^(?P<object_id>\d+)/$', 'relationtype_trackback',
                           name='relationapp_relationtype_trackback'),
                       )
