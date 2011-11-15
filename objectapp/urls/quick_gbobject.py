"""Url for the Objectapp quick gbobject view"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('objectapp.views.quick_gbobject',
                       url(r'^quick_gbobject/$', 'view_quick_gbobject',
                           name='objectapp_gbobject_quick_post')
                       )
