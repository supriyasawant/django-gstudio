"""Urls for the Relationapp sitemap"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('relationapp.views.sitemap',
                       url(r'^$', 'sitemap',
                           {'template': 'relationapp/sitemap.html'},
                           name='relationapp_sitemap'),
                       )
