"""Urls for the Attributeapp sitemap"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns

urlpatterns = patterns('attributeapp.views.sitemap',
                       url(r'^$', 'sitemap',
                           {'template': 'attributeapp/sitemap.html'},
                           name='attributeapp_sitemap'),
                       )
