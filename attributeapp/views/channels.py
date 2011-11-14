"""Views for Attributeapp channels"""
from django.views.generic.list_detail import object_list

from attributeapp.models import Attributetype


def attributetype_channel(request, query, *ka, **kw):
    """Display a custom selection of attributetypes"""
    queryset = Attributetype.published.search(query)
    return object_list(request, queryset=queryset,
                       *ka, **kw)
