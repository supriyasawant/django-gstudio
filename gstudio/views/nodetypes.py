"""Views for Gstudio nodetypes"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from gstudio.models import Nodetype
from gstudio.views.decorators import protect_nodetype
from gstudio.views.decorators import update_queryset


nodetype_index = update_queryset(object_list, Nodetype.published.all)

nodetype_year = update_queryset(archive_year, Nodetype.published.all)

nodetype_month = update_queryset(archive_month, Nodetype.published.all)

nodetype_day = update_queryset(archive_day, Nodetype.published.all)

nodetype_detail = protect_nodetype(object_detail)


def nodetype_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Nodetype,
    accordingly to 'object_id' argument
    """
    nodetype = get_object_or_404(Nodetype, pk=object_id)
    return redirect(nodetype, permanent=True)
