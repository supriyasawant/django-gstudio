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
def password(request, objecttype):
    """Displays the password form and handle validation
    by setting the valid password in a cookie."""
    error = False
    if request.method == 'POST':
        if request.POST.get('password') == objecttype.password:
            request.session[
                'gstudio_objecttype_%s_password' % objecttype.pk] = objecttype.password
            return redirect(objecttype)
        error = True
    return render_to_response('gstudio/password.html', {'error': error},
                              context_instance=RequestContext(request))


def protect_objecttype(view):
    """Decorator performing a security check if needed
    around the generic.date_based.objecttype_detail view
    and specify the template used to render the objecttype"""

    @wraps(view)
    def wrapper(*ka, **kw):
        """Do security check and retrieve the template"""
        request = ka[0]
        objecttype = get_object_or_404(kw['queryset'], slug=kw['slug'],
                                  creation_date__year=kw['year'],
                                  creation_date__month=kw['month'],
                                  creation_date__day=kw['day'])

        if objecttype.login_required and not request.user.is_authenticated():
            return login(request, 'gstudio/login.html')
        if objecttype.password and objecttype.password != \
               request.session.get('gstudio_objecttype_%s_password' % objecttype.pk):
            return password(request, objecttype)
        kw['template_name'] = objecttype.template
        return view(*ka, **kw)

    return wrapper


def template_name_for_objecttype_queryset_filtered(model_type, model_name):
    """Return a custom template name for views
    returning a queryset of Objecttype filtered by another model."""
    template_name_list = (
        'gstudio/%s/%s/objecttype_list.html' % (model_type, model_name),
        'gstudio/%s/%s_objecttype_list.html' % (model_type, model_name),
        'gstudio/%s/objecttype_list.html' % model_type,
        'gstudio/objecttype_list.html')

    for template_name in template_name_list:
        try:
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            continue
