"""Views for Gstudio objecttypes search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from gstudio.models import Objecttype
from gstudio.settings import PAGINATION


def objecttype_search(request):
    """Search objecttypes matching with a pattern"""
    error = None
    pattern = None
    objecttypes = Objecttype.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            objecttypes = Objecttype.published.search(pattern)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=objecttypes,
                       paginate_by=PAGINATION,
                       template_name='gstudio/objecttype_search.html',
                       extra_context={'error': error,
                                      'pattern': pattern})
