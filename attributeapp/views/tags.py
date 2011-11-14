"""Views for Attributeapp tags"""
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.template.defaultfilters import slugify

from tagging.models import Tag
from tagging.views import tagged_object_list

from attributeapp.models import Attributetype
from attributeapp.settings import PAGINATION

from attributeapp.views.decorators import template_name_for_attributetype_queryset_filtered


def tag_list(request, template_name='attributeapp/tag_list.html'):
    """Return the list of published tags with counts,
    try to simulate an object_list view"""
    tag_list = Tag.objects.usage_for_queryset(
        Attributetype.published.all(), counts=True)
    return render_to_response(template_name, {'object_list': tag_list},
                              context_instance=RequestContext(request))


def tag_detail(request, tag, page=None, **kwargs):
    """Display the attributetypes of a tag"""
    if not kwargs.get('template_name'):
        kwargs['template_name'] = template_name_for_attributetype_queryset_filtered(
            'tag', slugify(tag))

    return tagged_object_list(request, tag=tag,
                              queryset_or_model=Attributetype.published.all(),
                              paginate_by=PAGINATION, page=page,
                              **kwargs)
