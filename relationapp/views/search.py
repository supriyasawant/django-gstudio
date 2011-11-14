"""Views for Relationapp relationtypes search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from relationapp.models import Relationtype
from relationapp.settings import PAGINATION


def relationtype_search(request):
    """Search relationtypes matching with a pattern"""
    error = None
    pattern = None
    relationtypes = Relationtype.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            relationtypes = Relationtype.published.search(pattern)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=relationtypes,
                       paginate_by=PAGINATION,
                       template_name='relationapp/relationtype_search.html',
                       extra_context={'error': error,
                                      'pattern': pattern})
