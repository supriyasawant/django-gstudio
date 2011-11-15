"""Urls for the Attributeapp discussions"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^success/$', 'direct_to_template',
                           {'template': 'comments/attributeapp/attributetype/posted.html'},
                           name='attributeapp_discussion_success'),
                       )
