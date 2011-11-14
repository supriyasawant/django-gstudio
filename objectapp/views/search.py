"""Views for Objectapp gbobjects search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from objectapp.models import GBObject
from objectapp.settings import PAGINATION


def gbobject_search(request):
    """Search gbobjects matching with a pattern"""
    error = None
    pattern = None
    gbobjects = GBObject.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            gbobjects = GBObject.published.search(pattern)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=gbobjects,
                       paginate_by=PAGINATION,
                       template_name='objectapp/gbobject_search.html',
                       extra_context={'error': error,
                                      'pattern': pattern})
