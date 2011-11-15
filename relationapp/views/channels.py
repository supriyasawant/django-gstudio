"""Views for Relationapp channels"""
from django.views.generic.list_detail import object_list

from relationapp.models import Relationtype


def relationtype_channel(request, query, *ka, **kw):
    """Display a custom selection of relationtypes"""
    queryset = Relationtype.published.search(query)
    return object_list(request, queryset=queryset,
                       *ka, **kw)
