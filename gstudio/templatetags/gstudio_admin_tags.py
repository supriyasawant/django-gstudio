"""Template tags and filters for Gstudio's admin"""
from django.template import Library
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType

from gstudio.models import Objecttype
from gstudio.models import Author
from gstudio.models import Metatype
from gstudio.managers import DRAFT
from gstudio.managers import tags_published

register = Library()


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_draft_objecttypes(
    number=5, template='admin/gstudio/widgets/_draft_objecttypes.html'):
    """Return the latest draft objecttypes"""
    return {'template': template,
            'objecttypes': Objecttype.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_content_stats(
    template='admin/gstudio/widgets/_content_stats.html'):
    """Return statistics of the contents"""
    content_type = ContentType.objects.get_for_model(Objecttype)

    discussions = comments.get_model().objects.filter(
        is_public=True, content_type=content_type)

    return {'template': template,
            'objecttypes': Objecttype.published.count(),
            'metatypes': Metatype.objects.count(),
            'tags': tags_published().count(),
            'authors': Author.published.count(),
            'comments': discussions.filter(flags=None).count(),
            'pingbacks': discussions.filter(flags__flag='pingback').count(),
            'trackbacks': discussions.filter(flags__flag='trackback').count(),
            'rejects': comments.get_model().objects.filter(
                is_public=False, content_type=content_type).count(),
            }
