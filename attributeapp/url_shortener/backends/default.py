"""Default url shortener backend for Attributeapp"""
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from attributeapp.settings import PROTOCOL


def backend(attributetype):
    """Default url shortener backend for Attributeapp"""
    return '%s://%s%s' % (PROTOCOL, Site.objects.get_current().domain,
                       reverse('attributeapp_attributetype_shortlink', args=[attributetype.pk]))
