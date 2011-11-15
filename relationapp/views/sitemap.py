"""Views for Relationapp sitemap"""
from django.views.generic.simple import direct_to_template

from relationapp.models import Relationtype
from relationapp.models import Relation


def sitemap(*ka, **kw):
    """Wrapper around the direct to template generic view to
    force the update of the extra context"""
    kw['extra_context'] = {'relationtypes': Relationtype.tree.all(),
                           'relations': Relation.tree.all()}
    return direct_to_template(*ka, **kw)
