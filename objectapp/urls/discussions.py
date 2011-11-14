"""Urls for the Objectapp discussions"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^success/$', 'direct_to_template',
                           {'template': 'comments/objectapp/gbobject/posted.html'},
                           name='objectapp_discussion_success'),
                       )
