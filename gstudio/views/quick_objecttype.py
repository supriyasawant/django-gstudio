"""Views for Gstudio quick objecttype"""
from urllib import urlencode

from django import forms
from django.utils.html import linebreaks
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from gstudio.models import Objecttype
from gstudio.managers import DRAFT
from gstudio.managers import PUBLISHED


class QuickObjecttypeForm(forms.Form):
    """Form for posting an objecttype quickly"""

    title = forms.CharField(required=True, max_length=255)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False, max_length=255)


@permission_required('gstudio.add_objecttype')
def view_quick_objecttype(request):
    """View for quickly post an Objecttype"""
    if request.POST:
        form = QuickObjecttypeForm(request.POST)
        if form.is_valid():
            objecttype_dict = form.cleaned_data
            status = PUBLISHED
            if 'save_draft' in request.POST:
                status = DRAFT
            objecttype_dict['content'] = linebreaks(objecttype_dict['content'])
            objecttype_dict['slug'] = slugify(objecttype_dict['title'])
            objecttype_dict['status'] = status
            objecttype = Objecttype.objects.create(**objecttype_dict)
            objecttype.sites.add(Site.objects.get_current())
            objecttype.authors.add(request.user)
            return redirect(objecttype)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get(
                    'content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:gstudio_objecttype_add'),
                                   urlencode(data)))

    return redirect('admin:gstudio_objecttype_add')
