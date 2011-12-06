"""Views for Gstudio nodetypes search"""
from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_list

from gstudio.models import Nodetype
from gstudio.settings import PAGINATION


def nodetype_search(request):
    """Search nodetypes matching with a pattern"""
    error = None
    pattern = None
    nodetypes = Nodetype.published.none()

    if request.GET:
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            error = _('The pattern is too short')
        else:
            nodetypes = Nodetype.published.search(pattern)
    else:
        error = _('No pattern to search found')

    return object_list(request, queryset=nodetypes,
                       paginate_by=PAGINATION,
                       template_name='gstudio/nodetype_search.html',
                       extra_context={'error': error,
                                      'pattern': pattern})
