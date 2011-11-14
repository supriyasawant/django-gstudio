"""Template tags and filters for Objectapp's admin"""
from django.template import Library
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType

from objectapp.models import GBObject
from objectapp.models import Author
from objectapp.models import Objecttype
from objectapp.managers import DRAFT
from objectapp.managers import tags_published

register = Library()


@register.inclusion_tag('objectapp/tags/dummy.html')
def get_draft_gbobjects(
    number=5, template='admin/objectapp/widgets/_draft_gbobjects.html'):
    """Return the latest draft gbobjects"""
    return {'template': template,
            'gbobjects': GBObject.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('objectapp/tags/dummy.html')
def get_content_stats(
    template='admin/objectapp/widgets/_content_stats.html'):
    """Return statistics of the contents"""
    content_type = ContentType.objects.get_for_model(GBObject)

    discussions = comments.get_model().objects.filter(
        is_public=True, content_type=content_type)

    return {'template': template,
            'gbobjects': GBObject.published.count(),
            'objecttypes': Objecttype.objects.count(),
            'tags': tags_published().count(),
            'authors': Author.published.count(),
            'comments': discussions.filter(flags=None).count(),
            'pingbacks': discussions.filter(flags__flag='pingback').count(),
            'trackbacks': discussions.filter(flags__flag='trackback').count(),
            'rejects': comments.get_model().objects.filter(
                is_public=False, content_type=content_type).count(),
            }
