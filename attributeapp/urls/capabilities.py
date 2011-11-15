"""Urls for the attributeapp capabilities"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.contrib.sites.models import Site

from attributeapp.settings import PROTOCOL
from attributeapp.settings import COPYRIGHT
from attributeapp.settings import FEEDS_FORMAT

extra_context = {'protocol': PROTOCOL,
                 'site': Site.objects.get_current()}

extra_context_opensearch = extra_context.copy()
extra_context_opensearch.update({'copyright': COPYRIGHT,
                                 'feeds_format': FEEDS_FORMAT})

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^rsd.xml$', 'direct_to_template',
                           {'template': 'attributeapp/rsd.xml',
                            'mimetype': 'application/rsd+xml',
                            'extra_context': extra_context},
                           name='attributeapp_rsd'),
                       url(r'^wlwmanifest.xml$', 'direct_to_template',
                           {'template': 'attributeapp/wlwmanifest.xml',
                            'mimetype': 'application/wlwmanifest+xml',
                            'extra_context': extra_context},
                           name='attributeapp_wlwmanifest'),
                       url(r'^opensearch.xml$', 'direct_to_template',
                           {'template': 'attributeapp/opensearch.xml',
                            'mimetype':
                            'application/opensearchdescription+xml',
                            'extra_context': extra_context_opensearch},
                           name='attributeapp_opensearch'),
                       )
