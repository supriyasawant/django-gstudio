"""Views for Gstudio objecttypes"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from gstudio.models import Objecttype
from gstudio.views.decorators import protect_objecttype
from gstudio.views.decorators import update_queryset


objecttype_index = update_queryset(object_list, Objecttype.published.all)

objecttype_year = update_queryset(archive_year, Objecttype.published.all)

objecttype_month = update_queryset(archive_month, Objecttype.published.all)

objecttype_day = update_queryset(archive_day, Objecttype.published.all)

objecttype_detail = protect_objecttype(object_detail)


def objecttype_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Objecttype,
    accordingly to 'object_id' argument
    """
    objecttype = get_object_or_404(Objecttype, pk=object_id)
    return redirect(objecttype, permanent=True)
