"""Default url shortener backend for Relationapp"""
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from relationapp.settings import PROTOCOL


def backend(relationtype):
    """Default url shortener backend for Relationapp"""
    return '%s://%s%s' % (PROTOCOL, Site.objects.get_current().domain,
                       reverse('relationapp_relationtype_shortlink', args=[relationtype.pk]))
