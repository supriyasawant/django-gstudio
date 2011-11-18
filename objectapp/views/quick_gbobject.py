"""Views for Objectapp quick gbobject"""
from urllib import urlencode

from django import forms
from django.utils.html import linebreaks
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from objectapp.models import Gbobject
from objectapp.managers import DRAFT
from objectapp.managers import PUBLISHED


class QuickGbobjectForm(forms.Form):
    """Form for posting an gbobject quickly"""

    title = forms.CharField(required=True, max_length=255)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False, max_length=255)


@permission_required('objectapp.add_gbobject')
def view_quick_gbobject(request):
    """View for quickly post an Gbobject"""
    if request.POST:
        form = QuickGbobjectForm(request.POST)
        if form.is_valid():
            gbobject_dict = form.cleaned_data
            status = PUBLISHED
            if 'save_draft' in request.POST:
                status = DRAFT
            gbobject_dict['content'] = linebreaks(gbobject_dict['content'])
            gbobject_dict['slug'] = slugify(gbobject_dict['title'])
            gbobject_dict['status'] = status
            gbobject = Gbobject.objects.create(**gbobject_dict)
            gbobject.sites.add(Site.objects.get_current())
            gbobject.authors.add(request.user)
            return redirect(gbobject)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get(
                    'content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:objectapp_gbobject_add'),
                                   urlencode(data)))

    return redirect('admin:objectapp_gbobject_add')
