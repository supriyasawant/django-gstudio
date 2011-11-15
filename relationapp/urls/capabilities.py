"""Urls for the relationapp capabilities"""
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.contrib.sites.models import Site

from relationapp.settings import PROTOCOL
from relationapp.settings import COPYRIGHT
from relationapp.settings import FEEDS_FORMAT

extra_context = {'protocol': PROTOCOL,
                 'site': Site.objects.get_current()}

extra_context_opensearch = extra_context.copy()
extra_context_opensearch.update({'copyright': COPYRIGHT,
                                 'feeds_format': FEEDS_FORMAT})

urlpatterns = patterns('django.views.generic.simple',
                       url(r'^rsd.xml$', 'direct_to_template',
                           {'template': 'relationapp/rsd.xml',
                            'mimetype': 'application/rsd+xml',
                            'extra_context': extra_context},
                           name='relationapp_rsd'),
                       url(r'^wlwmanifest.xml$', 'direct_to_template',
                           {'template': 'relationapp/wlwmanifest.xml',
                            'mimetype': 'application/wlwmanifest+xml',
                            'extra_context': extra_context},
                           name='relationapp_wlwmanifest'),
                       url(r'^opensearch.xml$', 'direct_to_template',
                           {'template': 'relationapp/opensearch.xml',
                            'mimetype':
                            'application/opensearchdescription+xml',
                            'extra_context': extra_context_opensearch},
                           name='relationapp_opensearch'),
                       )
