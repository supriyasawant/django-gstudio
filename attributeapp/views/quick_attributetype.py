"""Views for Attributeapp quick attributetype"""
from urllib import urlencode

from django import forms
from django.utils.html import linebreaks
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from attributeapp.models import Attributetype
from attributeapp.managers import DRAFT
from attributeapp.managers import PUBLISHED


class QuickAttributetypeForm(forms.Form):
    """Form for posting an attributetype quickly"""

    title = forms.CharField(required=True, max_length=255)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False, max_length=255)


@permission_required('attributeapp.add_attributetype')
def view_quick_attributetype(request):
    """View for quickly post an Attributetype"""
    if request.POST:
        form = QuickAttributetypeForm(request.POST)
        if form.is_valid():
            attributetype_dict = form.cleaned_data
            status = PUBLISHED
            if 'save_draft' in request.POST:
                status = DRAFT
            attributetype_dict['content'] = linebreaks(attributetype_dict['content'])
            attributetype_dict['slug'] = slugify(attributetype_dict['title'])
            attributetype_dict['status'] = status
            attributetype = Attributetype.objects.create(**attributetype_dict)
            attributetype.sites.add(Site.objects.get_current())
            attributetype.authors.add(request.user)
            return redirect(attributetype)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get(
                    'content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:attributeapp_attributetype_add'),
                                   urlencode(data)))

    return redirect('admin:attributeapp_attributetype_add')
