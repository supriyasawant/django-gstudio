"""Views for Gstudio channels"""
from django.views.generic.list_detail import object_list

from gstudio.models import Objecttype


def objecttype_channel(request, query, *ka, **kw):
    """Display a custom selection of objecttypes"""
    queryset = Objecttype.published.search(query)
    return object_list(request, queryset=queryset,
                       *ka, **kw)
