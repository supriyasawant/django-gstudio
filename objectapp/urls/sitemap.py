"""Urls for the Objectapp sitemap"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('objectapp.views.sitemap',
                       url(r'^$', 'sitemap',
                           {'template': 'objectapp/sitemap.html'},
                           name='objectapp_sitemap'),
                       )
