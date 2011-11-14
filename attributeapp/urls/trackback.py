"""Urls for the Attributeapp trackback"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('attributeapp.views.trackback',
                       url(r'^(?P<object_id>\d+)/$', 'attributetype_trackback',
                           name='attributeapp_attributetype_trackback'),
                       )
