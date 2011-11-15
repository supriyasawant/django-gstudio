"""Views for Relationapp relations"""
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from relationapp.models import Relation
from relationapp.settings import PAGINATION
from relationapp.views.decorators import template_name_for_relationtype_queryset_filtered


def get_relation_or_404(path):
    """Retrieve a Relation by a path"""
    path_bits = [p for p in path.split('/') if p]
    return get_object_or_404(Relation, slug=path_bits[-1])


def relation_detail(request, path, page=None, **kwargs):
    """Display the relationtypes of a relation"""
    extra_context = kwargs.pop('extra_context', {})

    relation = get_relation_or_404(path)
    if not kwargs.get('template_name'):
        kwargs['template_name'] = template_name_for_relationtype_queryset_filtered(
            'relation', relation.slug)

    extra_context.update({'relation': relation})
    kwargs['extra_context'] = extra_context

    return object_list(request, queryset=relation.relationtypes_published(),
                       paginate_by=PAGINATION, page=page,
                       **kwargs)
