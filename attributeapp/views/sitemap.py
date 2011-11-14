"""Views for Attributeapp sitemap"""
from django.views.generic.simple import direct_to_template

from attributeapp.models import Attributetype
from attributeapp.models import Attribute


def sitemap(*ka, **kw):
    """Wrapper around the direct to template generic view to
    force the update of the extra context"""
    kw['extra_context'] = {'attributetypes': Attributetype.tree.all(),
                           'attributes': Attribute.tree.all()}
    return direct_to_template(*ka, **kw)
