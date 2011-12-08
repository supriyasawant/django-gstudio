"""Views for Gstudio quick nodetype"""
from urllib import urlencode

from django import forms
from django.utils.html import linebreaks
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import permission_required

from gstudio.models import Nodetype
from gstudio.managers import DRAFT
from gstudio.managers import PUBLISHED


class QuickNodetypeForm(forms.Form):
    """Form for posting an nodetype quickly"""

    title = forms.CharField(required=True, max_length=255)
    content = forms.CharField(required=True)
    tags = forms.CharField(required=False, max_length=255)


@permission_required('gstudio.add_nodetype')
def view_quick_nodetype(request):
    """View for quickly post an Nodetype"""
    if request.POST:
        form = QuickNodetypeForm(request.POST)
        if form.is_valid():
            nodetype_dict = form.cleaned_data
            status = PUBLISHED
            if 'save_draft' in request.POST:
                status = DRAFT
            nodetype_dict['content'] = linebreaks(nodetype_dict['content'])
            nodetype_dict['slug'] = slugify(nodetype_dict['title'])
            nodetype_dict['status'] = status
            nodetype = Nodetype.objects.create(**nodetype_dict)
            nodetype.sites.add(Site.objects.get_current())
            nodetype.authors.add(request.user)
            return redirect(nodetype)

        data = {'title': smart_str(request.POST.get('title', '')),
                'content': smart_str(linebreaks(request.POST.get(
                    'content', ''))),
                'tags': smart_str(request.POST.get('tags', '')),
                'slug': slugify(request.POST.get('title', '')),
                'authors': request.user.pk,
                'sites': Site.objects.get_current().pk}
        return redirect('%s?%s' % (reverse('admin:gstudio_nodetype_add'),
                                   urlencode(data)))

    return redirect('admin:gstudio_nodetype_add')
