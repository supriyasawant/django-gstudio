"""Defaults urls for the Attributeapp project"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    '',
    url(r'^tags/', include('attributeapp.urls.tags',)),
    url(r'^feeds/', include('attributeapp.urls.feeds')),
    url(r'^authors/', include('attributeapp.urls.authors')),
    url(r'^attributes/', include('attributeapp.urls.attributes')),
    url(r'^search/', include('attributeapp.urls.search')),
    url(r'^sitemap/', include('attributeapp.urls.sitemap')),
    url(r'^trackback/', include('attributeapp.urls.trackback')),
    url(r'^discussions/', include('attributeapp.urls.discussions')),
    url(r'^', include('attributeapp.urls.quick_attributetype')),
    url(r'^', include('attributeapp.urls.capabilities')),
    url(r'^', include('attributeapp.urls.attributetypes')),
    )
