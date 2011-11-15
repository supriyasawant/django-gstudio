"""Attributeapp to WordPress command module"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

from tagging.models import Tag

from attributeapp import __version__
from attributeapp.settings import PROTOCOL
from attributeapp.models import Attributetype
from attributeapp.models import Attribute


class Command(NoArgsCommand):
    """Command object for exporting a Attributeapp blog
    into WordPress via a WordPress eXtended RSS (WXR) file."""
    help = 'Export Attributeapp to WXR file.'

    def handle_noargs(self, **options):
        site = Site.objects.get_current()
        blog_context = {'attributetypes': Attributetype.objects.all(),
                        'attributes': Attribute.objects.all(),
                        'tags': Tag.objects.usage_for_model(Attributetype),
                        'version': __version__,
                        'description': 'Blog exported for django-attributeapp',
                        'language': settings.LANGUAGE_CODE,
                        'site': site,
                        'site_url': '%s://%s' % (PROTOCOL, site.domain)}
        export = render_to_string('attributeapp/wxr.xml', blog_context)
        print smart_str(export)
