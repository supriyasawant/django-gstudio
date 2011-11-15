"""Template tags and filters for Attributeapp's admin"""
from django.template import Library
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType

from attributeapp.models import Attributetype
from attributeapp.models import Author
from attributeapp.models import Attribute
from attributeapp.managers import DRAFT
from attributeapp.managers import tags_published

register = Library()


@register.inclusion_tag('attributeapp/tags/dummy.html')
def get_draft_attributetypes(
    number=5, template='admin/attributeapp/widgets/_draft_attributetypes.html'):
    """Return the latest draft attributetypes"""
    return {'template': template,
            'attributetypes': Attributetype.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('attributeapp/tags/dummy.html')
def get_content_stats(
    template='admin/attributeapp/widgets/_content_stats.html'):
    """Return statistics of the contents"""
    content_type = ContentType.objects.get_for_model(Attributetype)

    discussions = comments.get_model().objects.filter(
        is_public=True, content_type=content_type)

    return {'template': template,
            'attributetypes': Attributetype.published.count(),
            'attributes': Attribute.objects.count(),
            'tags': tags_published().count(),
            'authors': Author.published.count(),
            'comments': discussions.filter(flags=None).count(),
            'pingbacks': discussions.filter(flags__flag='pingback').count(),
            'trackbacks': discussions.filter(flags__flag='trackback').count(),
            'rejects': comments.get_model().objects.filter(
                is_public=False, content_type=content_type).count(),
            }
