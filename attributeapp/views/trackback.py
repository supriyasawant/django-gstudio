"""Views for Attributeapp trackback"""
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.sites.models import Site
from django.contrib import comments
from django.views.decorators.csrf import csrf_exempt
from django.contrib.contenttypes.models import ContentType
from django.views.generic.simple import direct_to_template

from attributeapp.models import Attributetype


@csrf_exempt
def attributetype_trackback(request, object_id):
    """Set a TrackBack for an Attributetype"""
    attributetype = get_object_or_404(Attributetype.published, pk=object_id)

    if request.POST.get('url'):
        error = ''
        url = request.POST['url']
        site = Site.objects.get_current()

        if not attributetype.pingback_enabled:
            error = u'Trackback is not enabled for %s' % attributetype.title

        title = request.POST.get('title') or url
        excerpt = request.POST.get('excerpt') or title
        blog_name = request.POST.get('blog_name') or title

        if not error:
            comment, created = comments.get_model().objects.get_or_create(
                content_type=ContentType.objects.get_for_model(Attributetype),
                object_pk=attributetype.pk, site=site, user_url=url,
                user_name=blog_name, defaults={'comment': excerpt})
            if created:
                user = attributetype.authors.all()[0]
                comment.flags.create(user=user, flag='trackback')
            else:
                error = u'Trackback is already registered'

        return direct_to_template(request, 'attributeapp/attributetype_trackback.xml',
                                  mimetype='text/xml',
                                  extra_context={'error': error})

    return redirect(attributetype, permanent=True)
