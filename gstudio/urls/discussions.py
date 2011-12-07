"""Urls for the Gstudio discussions"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^success/$', 'direct_to_template',
                           {'template': 'comments/gstudio/nodetype/posted.html'},
                           name='gstudio_discussion_success'),
                       )
