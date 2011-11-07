"""Default url shortener backend for Gstudio"""
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from gstudio.settings import PROTOCOL


def backend(objecttype):
    """Default url shortener backend for Gstudio"""
    return '%s://%s%s' % (PROTOCOL, Site.objects.get_current().domain,
                       reverse('gstudio_objecttype_shortlink', args=[objecttype.pk]))
