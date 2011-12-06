"""Decorators for gstudio.views"""
from functools import wraps

from django.template import RequestContext
from django.contrib.auth.views import login
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache


def update_queryset(view, queryset,
                    queryset_parameter='queryset'):
    """Decorator around views based on a queryset
    passed in parameter, who will force the update
    of the queryset before executing the view.
    Related to issue http://code.djangoproject.com/ticket/8378"""

    @wraps(view)
    def wrapper(*args, **kwargs):
        """Regenerate the queryset before passing it to the view."""
        kwargs[queryset_parameter] = queryset()
        return view(*args, **kwargs)

    return wrapper


@csrf_protect
@never_cache
def password(request, nodetype):
    """Displays the password form and handle validation
    by setting the valid password in a cookie."""
    error = False
    if request.method == 'POST':
        if request.POST.get('password') == nodetype.password:
            request.session[
                'gstudio_nodetype_%s_password' % nodetype.pk] = nodetype.password
            return redirect(nodetype)
        error = True
    return render_to_response('gstudio/password.html', {'error': error},
                              context_instance=RequestContext(request))


def protect_nodetype(view):
    """Decorator performing a security check if needed
    around the generic.date_based.nodetype_detail view
    and specify the template used to render the nodetype"""

    @wraps(view)
    def wrapper(*ka, **kw):
        """Do security check and retrieve the template"""
        request = ka[0]
        nodetype = get_object_or_404(kw['queryset'], slug=kw['slug'],
                                  creation_date__year=kw['year'],
                                  creation_date__month=kw['month'],
                                  creation_date__day=kw['day'])

        if nodetype.login_required and not request.user.is_authenticated():
            return login(request, 'gstudio/login.html')
        if nodetype.password and nodetype.password != \
               request.session.get('gstudio_nodetype_%s_password' % nodetype.pk):
            return password(request, nodetype)
        kw['template_name'] = nodetype.template
        return view(*ka, **kw)

    return wrapper


def template_name_for_nodetype_queryset_filtered(model_type, model_name):
    """Return a custom template name for views
    returning a queryset of Nodetype filtered by another model."""
    template_name_list = (
        'gstudio/%s/%s/nodetype_list.html' % (model_type, model_name),
        'gstudio/%s/%s_nodetype_list.html' % (model_type, model_name),
        'gstudio/%s/nodetype_list.html' % model_type,
        'gstudio/nodetype_list.html')

    for template_name in template_name_list:
        try:
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            continue
