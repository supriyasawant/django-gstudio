"""Urls for the Objectapp trackback"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('objectapp.views.trackback',
                       url(r'^(?P<object_id>\d+)/$', 'gbobject_trackback',
                           name='objectapp_gbobject_trackback'),
                       )
