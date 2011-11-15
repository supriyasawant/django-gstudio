"""Views for Attributeapp attributetypes search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from attributeapp.models import Attributetype
from attributeapp.settings import PAGINATION


def attributetype_search(request):
    """Search attributetypes matching with a pattern"""
    error = None
    pattern = None
    attributetypes = Attributetype.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            attributetypes = Attributetype.published.search(pattern)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=attributetypes,
                       paginate_by=PAGINATION,
                       template_name='attributeapp/attributetype_search.html',
                       extra_context={'error': error,
                                      'pattern': pattern})
