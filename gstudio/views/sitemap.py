"""Views for Gstudio sitemap"""
from django.views.generic.simple import direct_to_template

from gstudio.models import Objecttype
from gstudio.models import Metatype


def sitemap(*ka, **kw):
    """Wrapper around the direct to template generic view to
    force the update of the extra context"""
    kw['extra_context'] = {'objecttypes': Objecttype.published.all(),
                           'metatypes': Metatype.tree.all()}
    return direct_to_template(*ka, **kw)
