"""Views for Objectapp gbobjects"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from objectapp.models import GBObject
from objectapp.views.decorators import protect_gbobject
from objectapp.views.decorators import update_queryset


gbobject_index = update_queryset(object_list, GBObject.published.all)

gbobject_year = update_queryset(archive_year, GBObject.published.all)

gbobject_month = update_queryset(archive_month, GBObject.published.all)

gbobject_day = update_queryset(archive_day, GBObject.published.all)

gbobject_detail = protect_gbobject(object_detail)


def gbobject_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an GBObject,
    accordingly to 'object_id' argument
    """
    gbobject = get_object_or_404(GBObject, pk=object_id)
    return redirect(gbobject, permanent=True)
