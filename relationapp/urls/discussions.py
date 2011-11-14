"""Urls for the Relationapp discussions"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^success/$', 'direct_to_template',
                           {'template': 'comments/relationapp/relationtype/posted.html'},
                           name='relationapp_discussion_success'),
                       )
