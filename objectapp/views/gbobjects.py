"""Views for Objectapp gbobjects"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from objectapp.models import Gbobject
from objectapp.views.decorators import protect_gbobject
from objectapp.views.decorators import update_queryset


gbobject_index = update_queryset(object_list, Gbobject.published.all)

gbobject_year = update_queryset(archive_year, Gbobject.published.all)

gbobject_month = update_queryset(archive_month, Gbobject.published.all)

gbobject_day = update_queryset(archive_day, Gbobject.published.all)

gbobject_detail = protect_gbobject(object_detail)


def gbobject_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Gbobject,
    accordingly to 'object_id' argument
    """
    gbobject = get_object_or_404(Gbobject, pk=object_id)
    return redirect(gbobject, permanent=True)
