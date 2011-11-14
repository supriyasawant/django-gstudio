"""Url for the Attributeapp quick attributetype view"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('attributeapp.views.quick_attributetype',
                       url(r'^quick_attributetype/$', 'view_quick_attributetype',
                           name='attributeapp_attributetype_quick_post')
                       )
