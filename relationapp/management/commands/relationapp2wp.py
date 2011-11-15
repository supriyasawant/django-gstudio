"""Relationapp to WordPress command module"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

from tagging.models import Tag

from relationapp import __version__
from relationapp.settings import PROTOCOL
from relationapp.models import Relationtype
from relationapp.models import Relation


class Command(NoArgsCommand):
    """Command object for exporting a Relationapp blog
    into WordPress via a WordPress eXtended RSS (WXR) file."""
    help = 'Export Relationapp to WXR file.'

    def handle_noargs(self, **options):
        site = Site.objects.get_current()
        blog_context = {'relationtypes': Relationtype.objects.all(),
                        'relations': Relation.objects.all(),
                        'tags': Tag.objects.usage_for_model(Relationtype),
                        'version': __version__,
                        'description': 'Blog exported for django-relationapp',
                        'language': settings.LANGUAGE_CODE,
                        'site': site,
                        'site_url': '%s://%s' % (PROTOCOL, site.domain)}
        export = render_to_string('relationapp/wxr.xml', blog_context)
        print smart_str(export)
