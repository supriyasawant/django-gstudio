"""Views for Attributeapp attributes"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from attributeapp.models import Attribute
from attributeapp.settings import PAGINATION
from attributeapp.views.decorators import template_name_for_attributetype_queryset_filtered


def get_attribute_or_404(path):
    """Retrieve a Attribute by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Attribute, slug=path_bits[-1])


def attribute_detail(request, path, page=None, **kwargs):
    """Display the attributetypes of a attribute"""
    extra_context = kwargs.pop('extra_context', {})

    attribute = get_attribute_or_404(path)
    if not kwargs.get('template_name'):
        kwargs['template_name'] = template_name_for_attributetype_queryset_filtered(
            'attribute', attribute.slug)

    extra_context.update({'attribute': attribute})
    kwargs['extra_context'] = extra_context

    return object_list(request, queryset=attribute.attributetypes_published(),
                       paginate_by=PAGINATION, page=page,
                       **kwargs)
