"""Views for Objectapp sitemap"""
from django.views.generic.simple import direct_to_template

from objectapp.models import GBObject
from objectapp.models import Objecttype


def sitemap(*ka, **kw):
    """Wrapper around the direct to template generic view to
    force the update of the extra context"""
    kw['extra_context'] = {'gbobjects': GBObject.tree.all(),
                           'objecttypes': Objecttype.tree.all()}
    return direct_to_template(*ka, **kw)
