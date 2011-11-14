"""Views for Relationapp relationtypes"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list
from django.views.generic.date_based import archive_year
from django.views.generic.date_based import archive_month
from django.views.generic.date_based import archive_day
from django.views.generic.date_based import object_detail

from relationapp.models import Relationtype
from relationapp.views.decorators import protect_relationtype
from relationapp.views.decorators import update_queryset


relationtype_index = update_queryset(object_list, Relationtype.published.all)

relationtype_year = update_queryset(archive_year, Relationtype.published.all)

relationtype_month = update_queryset(archive_month, Relationtype.published.all)

relationtype_day = update_queryset(archive_day, Relationtype.published.all)

relationtype_detail = protect_relationtype(object_detail)


def relationtype_shortlink(request, object_id):
    """
    Redirect to the 'get_absolute_url' of an Relationtype,
    accordingly to 'object_id' argument
    """
    relationtype = get_object_or_404(Relationtype, pk=object_id)
    return redirect(relationtype, permanent=True)
