"""Url for the Relationapp quick relationtype view"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('relationapp.views.quick_relationtype',
                       url(r'^quick_relationtype/$', 'view_quick_relationtype',
                           name='relationapp_relationtype_quick_post')
                       )
