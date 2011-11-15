"""Default url shortener backend for Objectapp"""
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse

from objectapp.settings import PROTOCOL


def backend(gbobject):
    """Default url shortener backend for Objectapp"""
    return '%s://%s%s' % (PROTOCOL, Site.objects.get_current().domain,
                       reverse('objectapp_gbobject_shortlink', args=[gbobject.pk]))
