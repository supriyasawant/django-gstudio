"""Decorators for objectapp.views"""
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
def password(request, gbobject):
    """Displays the password form and handle validation
    by setting the valid password in a cookie."""
    error = False
    if request.method == 'POST':
        if request.POST.get('password') == gbobject.password:
            request.session[
                'objectapp_gbobject_%s_password' % gbobject.pk] = gbobject.password
            return redirect(gbobject)
        error = True
    return render_to_response('objectapp/password.html', {'error': error},
                              context_instance=RequestContext(request))


def protect_gbobject(view):
    """Decorator performing a security check if needed
    around the generic.date_based.gbobject_detail view
    and specify the template used to render the gbobject"""

    @wraps(view)
    def wrapper(*ka, **kw):
        """Do security check and retrieve the template"""
        request = ka[0]
        gbobject = get_object_or_404(kw['queryset'], slug=kw['slug'],
                                  creation_date__year=kw['year'],
                                  creation_date__month=kw['month'],
                                  creation_date__day=kw['day'])

        if gbobject.login_required and not request.user.is_authenticated():
            return login(request, 'objectapp/login.html')
        if gbobject.password and gbobject.password != \
               request.session.get('objectapp_gbobject_%s_password' % gbobject.pk):
            return password(request, gbobject)
        kw['template_name'] = gbobject.template
        return view(*ka, **kw)

    return wrapper


def template_name_for_gbobject_queryset_filtered(model_type, model_name):
    """Return a custom template name for views
    returning a queryset of Gbobject filtered by another model."""
    template_name_list = (
        'objectapp/%s/%s/gbobject_list.html' % (model_type, model_name),
        'objectapp/%s/%s_gbobject_list.html' % (model_type, model_name),
        'objectapp/%s/gbobject_list.html' % model_type,
        'objectapp/gbobject_list.html')

    for template_name in template_name_list:
        try:
            get_template(template_name)
            return template_name
        except TemplateDoesNotExist:
            continue
