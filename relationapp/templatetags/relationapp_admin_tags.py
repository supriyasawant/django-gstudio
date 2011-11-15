"""Template tags and filters for Relationapp's admin"""
from django.template import Library
from django.contrib import comments
from django.contrib.contenttypes.models import ContentType

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.models import Relation
from relationapp.managers import DRAFT
from relationapp.managers import tags_published

register = Library()


@register.inclusion_tag('relationapp/tags/dummy.html')
def get_draft_relationtypes(
    number=5, template='admin/relationapp/widgets/_draft_relationtypes.html'):
    """Return the latest draft relationtypes"""
    return {'template': template,
            'relationtypes': Relationtype.objects.filter(status=DRAFT)[:number]}


@register.inclusion_tag('relationapp/tags/dummy.html')
def get_content_stats(
    template='admin/relationapp/widgets/_content_stats.html'):
    """Return statistics of the contents"""
    content_type = ContentType.objects.get_for_model(Relationtype)

    discussions = comments.get_model().objects.filter(
        is_public=True, content_type=content_type)

    return {'template': template,
            'relationtypes': Relationtype.published.count(),
            'relations': Relation.objects.count(),
            'tags': tags_published().count(),
            'authors': Author.published.count(),
            'comments': discussions.filter(flags=None).count(),
            'pingbacks': discussions.filter(flags__flag='pingback').count(),
            'trackbacks': discussions.filter(flags__flag='trackback').count(),
            'rejects': comments.get_model().objects.filter(
                is_public=False, content_type=content_type).count(),
            }
