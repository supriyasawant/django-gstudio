"""Url for the Gstudio quick objecttype view"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('gstudio.views.quick_objecttype',
                       url(r'^quick_objecttype/$', 'view_quick_objecttype',
                           name='gstudio_objecttype_quick_post')
                       )
