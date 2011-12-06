"""Views for Gstudio channels"""
from django.views.generic.list_detail import object_list

from gstudio.models import Nodetype


def nodetype_channel(request, query, *ka, **kw):
    """Display a custom selection of nodetypes"""
    queryset = Nodetype.published.search(query)
    return object_list(request, queryset=queryset,
                       *ka, **kw)
