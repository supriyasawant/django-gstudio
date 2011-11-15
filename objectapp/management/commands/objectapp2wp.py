"""Objectapp to WordPress command module"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

from tagging.models import Tag

from objectapp import __version__
from objectapp.settings import PROTOCOL
from objectapp.models import GBObject
from objectapp.models import Objecttype


class Command(NoArgsCommand):
    """Command object for exporting a Objectapp blog
    into WordPress via a WordPress eXtended RSS (WXR) file."""
    help = 'Export Objectapp to WXR file.'

    def handle_noargs(self, **options):
        site = Site.objects.get_current()
        blog_context = {'gbobjects': GBObject.objects.all(),
                        'objecttypes': Objecttype.objects.all(),
                        'tags': Tag.objects.usage_for_model(GBObject),
                        'version': __version__,
                        'description': 'Blog exported for django-objectapp',
                        'language': settings.LANGUAGE_CODE,
                        'site': site,
                        'site_url': '%s://%s' % (PROTOCOL, site.domain)}
        export = render_to_string('objectapp/wxr.xml', blog_context)
        print smart_str(export)
