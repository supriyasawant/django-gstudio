"""Views for Relationapp quick relationtype"""
from urllib import urlencode

from django import forms
from django.utils.html import linebreaks
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from relationapp.models import Relationtype
from relationapp.managers import DRAFT
from relationapp.managers import PUBLISHED


class QuickRelationtypeForm(forms.Form):
    """Form for posting an relationtype quickly"""

    title = forms.CharField(required=True, max_length=255)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False, max_length=255)


@permission_required('relationapp.add_relationtype')
def view_quick_relationtype(request):
    """View for quickly post an Relationtype"""
    if request.POST:
        form = QuickRelationtypeForm(request.POST)
        if form.is_valid():
            relationtype_dict = form.cleaned_data
            status = PUBLISHED
            if 'save_draft' in request.POST:
                status = DRAFT
            relationtype_dict['content'] = linebreaks(relationtype_dict['content'])
            relationtype_dict['slug'] = slugify(relationtype_dict['title'])
            relationtype_dict['status'] = status
            relationtype = Relationtype.objects.create(**relationtype_dict)
            relationtype.sites.add(Site.objects.get_current())
            relationtype.authors.add(request.user)
            return redirect(relationtype)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get(
                    'content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:relationapp_relationtype_add'),
                                   urlencode(data)))

    return redirect('admin:relationapp_relationtype_add')
