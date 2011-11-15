"""Views for Objectapp channels"""
from django.views.generic.list_detail import object_list

from objectapp.models import GBObject


def gbobject_channel(request, query, *ka, **kw):
    """Display a custom selection of gbobjects"""
    queryset = GBObject.published.search(query)
    return object_list(request, queryset=queryset,
                       *ka, **kw)
