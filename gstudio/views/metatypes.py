"""Views for Gstudio metatypes"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from gstudio.models import Metatype
from gstudio.settings import PAGINATION
from gstudio.views.decorators import template_name_for_objecttype_queryset_filtered


def get_metatype_or_404(path):
    """Retrieve a Metatype by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Metatype, slug=path_bits[-1])


def metatype_detail(request, path, page=None, **kwargs):
    """Display the objecttypes of a metatype"""
    extra_context = kwargs.pop('extra_context', {})

    metatype = get_metatype_or_404(path)
    if not kwargs.get('template_name'):
        kwargs['template_name'] = template_name_for_objecttype_queryset_filtered(
            'metatype', metatype.slug)

    extra_context.update({'metatype': metatype})
    kwargs['extra_context'] = extra_context

    return object_list(request, queryset=metatype.nodes_published(),
                       paginate_by=PAGINATION, page=page,
                       **kwargs)
