"""Gstudio to WordPress command module"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.management.base import NoArgsCommand

from tagging.models import Tag

from gstudio import __version__
from gstudio.settings import PROTOCOL
from gstudio.models import Nodetype
from gstudio.models import Metatype


class Command(NoArgsCommand):
    """Command object for exporting a Gstudio blog
    into WordPress via a WordPress eXtended RSS (WXR) file."""
    help = 'Export Gstudio to WXR file.'

    def handle_noargs(self, **options):
        site = Site.objects.get_current()
        blog_context = {'nodetypes': Nodetype.objects.all(),
                        'metatypes': Metatype.objects.all(),
                        'tags': Tag.objects.usage_for_model(Nodetype),
                        'version': __version__,
                        'description': 'Blog exported for django-gstudio',
                        'language': settings.LANGUAGE_CODE,
                        'site': site,
                        'site_url': '%s://%s' % (PROTOCOL, site.domain)}
        export = render_to_string('gstudio/wxr.xml', blog_context)
        print smart_str(export)
