"""Views for Attributeapp attributetypes"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from attributeapp.models import Attributetype
from attributeapp.views.decorators import protect_attributetype
from attributeapp.views.decorators import update_queryset


attributetype_index = update_queryset(object_list, Attributetype.published.all)

attributetype_year = update_queryset(archive_year, Attributetype.published.all)

attributetype_month = update_queryset(archive_month, Attributetype.published.all)

attributetype_day = update_queryset(archive_day, Attributetype.published.all)

attributetype_detail = protect_attributetype(object_detail)


def attributetype_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Attributetype,
    accordingly to 'object_id' argument
    """
    attributetype = get_object_or_404(Attributetype, pk=object_id)
    return redirect(attributetype, permanent=True)
