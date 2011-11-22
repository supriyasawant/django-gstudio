"""Views for Objectapp objecttypes"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from objectapp.models import Objecttype
from objectapp.settings import PAGINATION
from objectapp.views.decorators import template_name_for_gbobject_queryset_filtered


def get_Objecttype_or_404(path):
    """Retrieve a Objecttype by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Objecttype, slug=path_bits[-1])


def Objecttype_detail(request, path, page=None, **kwargs):
    """Display the gbobjects of a Objecttype"""
    extra_context = kwargs.pop('extra_context', {})

    Objecttype = get_Objecttype_or_404(path)
    if not kwargs.get('template_name'):
        kwargs['template_name'] = template_name_for_gbobject_queryset_filtered(
            'Objecttype', Objecttype.slug)

    extra_context.update({'Objecttype': Objecttype})
    kwargs['extra_context'] = extra_context

    return object_list(request, queryset=Objecttype.gbobjects_published(),
                       paginate_by=PAGINATION, page=page,
                       **kwargs)
