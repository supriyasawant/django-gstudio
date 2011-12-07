"""Url for the Gstudio quick nodetype view"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('gstudio.views.quick_nodetype',
                       url(r'^quick_nodetype/$', 'view_quick_nodetype',
                           name='gstudio_nodetype_quick_post')
                       )
