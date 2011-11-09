"""Template tags and filters for Gstudio"""
from hashlib import md5
from random import sample
from urllib import urlencode
from datetime import datetime

from django.db.models import Q
from django.db import connection
from django.template import Node
from django.template import Library
from django.template import TemplateSyntaxError
from django.contrib.comments.models import CommentFlag
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import smart_unicode
from django.contrib.comments import get_model as get_comment_model

from tagging.models import Tag
from tagging.utils import calculate_cloud

from gstudio.models import Objecttype
from gstudio.models import Author
from gstudio.models import Metatype
from gstudio.managers import tags_published
from gstudio.comparison import VectorBuilder
from gstudio.comparison import pearson_score
from gstudio.templatetags.zcalendar import GstudioCalendar
from gstudio.templatetags.zbreadcrumbs import retrieve_breadcrumbs

register = Library()

VECTORS = None
VECTORS_FACTORY = lambda: VectorBuilder(Objecttype.published.all(),
                                        ['title', 'excerpt', 'content'])
CACHE_OBJECTTYPES_RELATED = {}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_metatypes(template='gstudio/tags/metatypes.html'):
    """Return the metatypes"""
    return {'template': template,
            'metatypes': Metatype.tree.all()}

#@register.inclusion_tag('gstudio/tags/dummy.html')
#def get_subtypes(template='gstudio/tags/objecttypes.html'):
#    """Return the subtypes"""
#    return {'template': template,
#            'subtypes': Objecttype.tree.all()}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_authors(template='gstudio/tags/authors.html'):
    """Return the published authors"""
    return {'template': template,
            'authors': Author.published.all()}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_recent_objecttypes(number=5, template='gstudio/tags/recent_objecttypes.html'):
    """Return the most recent objecttypes"""
    return {'template': template,
            'objecttypes': Objecttype.published.all()[:number]}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_featured_objecttypes(number=5,
                         template='gstudio/tags/featured_objecttypes.html'):
    """Return the featured objecttypes"""
    return {'template': template,
            'objecttypes': Objecttype.published.filter(featured=True)[:number]}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_random_objecttypes(number=5, template='gstudio/tags/random_objecttypes.html'):
    """Return random objecttypes"""
    objecttypes = Objecttype.published.all()
    if number > len(objecttypes):
        number = len(objecttypes)
    return {'template': template,
            'objecttypes': sample(objecttypes, number)}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_popular_objecttypes(number=5, template='gstudio/tags/popular_objecttypes.html'):
    """Return popular  objecttypes"""
    ctype = ContentType.objects.get_for_model(Objecttype)
    query = """SELECT object_pk, COUNT(*) AS score
    FROM %s
    WHERE content_type_id = %%s
    AND is_public = '1'
    GROUP BY object_pk
    ORDER BY score DESC""" % get_comment_model()._meta.db_table

    cursor = connection.cursor()
    cursor.execute(query, [ctype.id])
    object_ids = [int(row[0]) for row in cursor.fetchall()]

    # Use ``in_bulk`` here instead of an ``id__in`` filter, because ``id__in``
    # would clobber the ordering.
    object_dict = Objecttype.published.in_bulk(object_ids)

    return {'template': template,
            'objecttypes': [object_dict[object_id]
                        for object_id in object_ids
                        if object_id in object_dict][:number]}


@register.inclusion_tag('gstudio/tags/dummy.html', takes_context=True)
def get_similar_objecttypes(context, number=5,
                        template='gstudio/tags/similar_objecttypes.html',
                        flush=False):
    """Return similar objecttypes"""
    global VECTORS
    global CACHE_OBJECTTYPES_RELATED

    if VECTORS is None or flush:
        VECTORS = VECTORS_FACTORY()
        CACHE_OBJECTTYPES_RELATED = {}

    def compute_related(object_id, dataset):
        """Compute related objecttypes to an objecttype with a dataset"""
        object_vector = None
        for objecttype, e_vector in dataset.items():
            if objecttype.pk == object_id:
                object_vector = e_vector

        if not object_vector:
            return []

        objecttype_related = {}
        for objecttype, e_vector in dataset.items():
            if objecttype.pk != object_id:
                score = pearson_score(object_vector, e_vector)
                if score:
                    objecttype_related[objecttype] = score

        related = sorted(objecttype_related.items(), key=lambda(k, v): (v, k))
        return [rel[0] for rel in related]

    object_id = context['object'].pk
    columns, dataset = VECTORS()
    key = '%s-%s' % (object_id, VECTORS.key)
    if not key in CACHE_OBJECTTYPES_RELATED.keys():
        CACHE_OBJECTTYPES_RELATED[key] = compute_related(object_id, dataset)

    objecttypes = CACHE_OBJECTTYPES_RELATED[key][:number]
    return {'template': template,
            'objecttypes': objecttypes}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_archives_objecttypes(template='gstudio/tags/archives_objecttypes.html'):
    """Return archives objecttypes"""
    return {'template': template,
            'archives': Objecttype.published.dates('creation_date', 'month',
                                              order='DESC')}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_archives_objecttypes_tree(
    template='gstudio/tags/archives_objecttypes_tree.html'):
    """Return archives objecttypes as a Tree"""
    return {'template': template,
            'archives': Objecttype.published.dates('creation_date', 'day',
                                              order='ASC')}


@register.inclusion_tag('gstudio/tags/dummy.html', takes_context=True)
def get_calendar_objecttypes(context, year=None, month=None,
                         template='gstudio/tags/calendar.html'):
    """Return an HTML calendar of objecttypes"""
    if not year or not month:
        date_month = context.get('month') or context.get('day') or \
                     getattr(context.get('object'), 'creation_date', None) or \
                     datetime.today()
        year, month = date_month.timetuple()[:2]

    calendar = GstudioCalendar()
    current_month = datetime(year, month, 1)

    dates = list(Objecttype.published.dates('creation_date', 'month'))

    if not current_month in dates:
        dates.append(current_month)
        dates.sort()
    index = dates.index(current_month)

    previous_month = index > 0 and dates[index - 1] or None
    next_month = index != len(dates) - 1 and dates[index + 1] or None

    return {'template': template,
            'next_month': next_month,
            'previous_month': previous_month,
            'calendar': calendar.formatmonth(year, month)}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_recent_comments(number=5, template='gstudio/tags/recent_comments.html'):
    """Return the most recent comments"""
    # Using map(smart_unicode... fix bug related to issue #8554
    objecttype_published_pks = map(smart_unicode,
                              Objecttype.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Objecttype)

    comments = get_comment_model().objects.filter(
        Q(flags=None) | Q(flags__flag=CommentFlag.MODERATOR_APPROVAL),
        content_type=content_type, object_pk__in=objecttype_published_pks,
        is_public=True).order_by('-submit_date')[:number]

    return {'template': template,
            'comments': comments}


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_recent_linkbacks(number=5,
                         template='gstudio/tags/recent_linkbacks.html'):
    """Return the most recent linkbacks"""
    objecttype_published_pks = map(smart_unicode,
                              Objecttype.published.values_list('id', flat=True))
    content_type = ContentType.objects.get_for_model(Objecttype)

    linkbacks = get_comment_model().objects.filter(
        content_type=content_type,
        object_pk__in=objecttype_published_pks,
        flags__flag__in=['pingback', 'trackback'],
        is_public=True).order_by(
        '-submit_date')[:number]

    return {'template': template,
            'linkbacks': linkbacks}


@register.inclusion_tag('gstudio/tags/dummy.html', takes_context=True)
def gstudio_pagination(context, page, begin_pages=3, end_pages=3,
                      before_pages=2, after_pages=2,
                      template='gstudio/tags/pagination.html'):
    """Return a Digg-like pagination, by splitting long list of page
    into 3 blocks of pages"""
    GET_string = ''
    for key, value in context['request'].GET.items():
        if key != 'page':
            GET_string += '&%s=%s' % (key, value)

    begin = page.paginator.page_range[:begin_pages]
    end = page.paginator.page_range[-end_pages:]
    middle = page.paginator.page_range[max(page.number - before_pages - 1, 0):
                                       page.number + after_pages]

    if set(begin) & set(end):  # [1, 2, 3], [...], [2, 3, 4]
        begin = sorted(set(begin + end))  # [1, 2, 3, 4]
        middle, end = [], []
    elif begin[-1] + 1 == end[0]:  # [1, 2, 3], [...], [4, 5, 6]
        begin += end  # [1, 2, 3, 4, 5, 6]
        middle, end = [], []
    elif set(begin) & set(middle):  # [1, 2, 3], [2, 3, 4], [...]
        begin = sorted(set(begin + middle))  # [1, 2, 3, 4]
        middle = []
    elif begin[-1] + 1 == middle[0]:  # [1, 2, 3], [4, 5, 6], [...]
        begin += middle  # [1, 2, 3, 4, 5, 6]
        middle = []
    elif middle[-1] + 1 == end[0]:  # [...], [15, 16, 17], [18, 19, 20]
        end = middle + end  # [15, 16, 17, 18, 19, 20]
        middle = []
    elif set(middle) & set(end):  # [...], [17, 18, 19], [18, 19, 20]
        end = sorted(set(middle + end))  # [17, 18, 19, 20]
        middle = []

    return {'template': template, 'page': page, 'GET_string': GET_string,
            'begin': begin, 'middle': middle, 'end': end}


@register.inclusion_tag('gstudio/tags/dummy.html', takes_context=True)
def gstudio_breadcrumbs(context, separator='/', root_name='Nodes',
                       template='gstudio/tags/breadcrumbs.html',):
    """Return a breadcrumb for the application"""
    path = context['request'].path
    page_object = context.get('object') or context.get('metatype') or \
                  context.get('tag') or context.get('author')
    breadcrumbs = retrieve_breadcrumbs(path, page_object, root_name)

    return {'template': template,
            'separator': separator,
            'breadcrumbs': breadcrumbs}


@register.simple_tag
def get_gravatar(email, size=80, rating='g', default=None):
    """Return url for a Gravatar"""
    url = 'http://www.gravatar.com/avatar/%s.jpg' % \
          md5(email.strip().lower()).hexdigest()
    options = {'s': size, 'r': rating}
    if default:
        options['d'] = default

    url = '%s?%s' % (url, urlencode(options))
    return url.replace('&', '&amp;')


class TagsNode(Node):
    def __init__(self, context_var):
        self.context_var = context_var

    def render(self, context):
        context[self.context_var] = tags_published()
        return ''


@register.tag
def get_tags(parser, token):
    """{% get_tags as var %}"""
    bits = token.split_contents()

    if len(bits) != 3:
        raise TemplateSyntaxError(
            'get_tags tag takes exactly two arguments')
    if bits[1] != 'as':
        raise TemplateSyntaxError(
            "first argument to get_tags tag must be 'as'")
    return TagsNode(bits[2])


@register.inclusion_tag('gstudio/tags/dummy.html')
def get_tag_cloud(steps=6, template='gstudio/tags/tag_cloud.html'):
    """Return a cloud of published tags"""
    tags = Tag.objects.usage_for_queryset(
        Objecttype.published.all(), counts=True)
    return {'template': template,
            'tags': calculate_cloud(tags, steps)}
