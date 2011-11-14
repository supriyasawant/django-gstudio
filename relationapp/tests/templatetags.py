"""Test cases for Relationapp's templatetags"""
from datetime import datetime

from django.test import TestCase
from django.template import Context
from django.template import Template
from django.template import TemplateSyntaxError
from django.contrib import comments
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.comments.models import CommentFlag

from tagging.models import Tag

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.models import Relation
from relationapp.managers import DRAFT
from relationapp.managers import PUBLISHED
from relationapp.templatetags.relationapp_tags import get_authors
from relationapp.templatetags.relationapp_tags import get_gravatar
from relationapp.templatetags.relationapp_tags import get_tag_cloud
from relationapp.templatetags.relationapp_tags import get_relations
from relationapp.templatetags.relationapp_tags import relationapp_pagination
from relationapp.templatetags.relationapp_tags import get_recent_relationtypes
from relationapp.templatetags.relationapp_tags import get_random_relationtypes
from relationapp.templatetags.relationapp_tags import relationapp_breadcrumbs
from relationapp.templatetags.relationapp_tags import get_popular_relationtypes
from relationapp.templatetags.relationapp_tags import get_similar_relationtypes
from relationapp.templatetags.relationapp_tags import get_recent_comments
from relationapp.templatetags.relationapp_tags import get_recent_linkbacks
from relationapp.templatetags.relationapp_tags import get_calendar_relationtypes
from relationapp.templatetags.relationapp_tags import get_archives_relationtypes
from relationapp.templatetags.relationapp_tags import get_featured_relationtypes
from relationapp.templatetags.relationapp_tags import get_archives_relationtypes_tree


class TemplateTagsTestCase(TestCase):
    """Test cases for Template tags"""

    def setUp(self):
        params = {'title': 'My relationtype',
                  'content': 'My content',
                  'tags': 'relationapp, test',
                  'creation_date': datetime(2010, 1, 1),
                  'slug': 'my-relationtype'}
        self.relationtype = Relationtype.objects.create(**params)

    def publish_relationtype(self):
        self.relationtype.status = PUBLISHED
        self.relationtype.featured = True
        self.relationtype.sites.add(Site.objects.get_current())
        self.relationtype.save()

    def test_get_relations(self):
        context = get_relations()
        self.assertEquals(len(context['relations']), 0)
        self.assertEquals(context['template'], 'relationapp/tags/relations.html')

        Relation.objects.create(title='Relation 1', slug='relation-1')
        context = get_relations('custom_template.html')
        self.assertEquals(len(context['relations']), 1)
        self.assertEquals(context['template'], 'custom_template.html')

    def test_get_authors(self):
        context = get_authors()
        self.assertEquals(len(context['authors']), 0)
        self.assertEquals(context['template'], 'relationapp/tags/authors.html')

        user = User.objects.create_user(username='webmaster',
                                        email='webmaster@example.com')
        self.relationtype.authors.add(user)
        self.publish_relationtype()
        context = get_authors('custom_template.html')
        self.assertEquals(len(context['authors']), 1)
        self.assertEquals(context['template'], 'custom_template.html')

    def test_get_recent_relationtypes(self):
        context = get_recent_relationtypes()
        self.assertEquals(len(context['relationtypes']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/recent_relationtypes.html')

        self.publish_relationtype()
        context = get_recent_relationtypes(3, 'custom_template.html')
        self.assertEquals(len(context['relationtypes']), 1)
        self.assertEquals(context['template'], 'custom_template.html')
        context = get_recent_relationtypes(0)
        self.assertEquals(len(context['relationtypes']), 0)

    def test_get_featured_relationtypes(self):
        context = get_featured_relationtypes()
        self.assertEquals(len(context['relationtypes']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/featured_relationtypes.html')

        self.publish_relationtype()
        context = get_featured_relationtypes(3, 'custom_template.html')
        self.assertEquals(len(context['relationtypes']), 1)
        self.assertEquals(context['template'], 'custom_template.html')
        context = get_featured_relationtypes(0)
        self.assertEquals(len(context['relationtypes']), 0)

    def test_get_random_relationtypes(self):
        context = get_random_relationtypes()
        self.assertEquals(len(context['relationtypes']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/random_relationtypes.html')

        self.publish_relationtype()
        context = get_random_relationtypes(3, 'custom_template.html')
        self.assertEquals(len(context['relationtypes']), 1)
        self.assertEquals(context['template'], 'custom_template.html')
        context = get_random_relationtypes(0)
        self.assertEquals(len(context['relationtypes']), 0)

    def test_get_popular_relationtypes(self):
        context = get_popular_relationtypes()
        self.assertEquals(len(context['relationtypes']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/popular_relationtypes.html')

        self.publish_relationtype()
        context = get_popular_relationtypes(3, 'custom_template.html')
        self.assertEquals(len(context['relationtypes']), 0)
        self.assertEquals(context['template'], 'custom_template.html')

        params = {'title': 'My second relationtype',
                  'content': 'My second content',
                  'tags': 'relationapp, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-relationtype'}
        site = Site.objects.get_current()
        second_relationtype = Relationtype.objects.create(**params)
        second_relationtype.sites.add(site)

        comments.get_model().objects.create(comment='My Comment 1', site=site,
                                            content_object=self.relationtype)
        comments.get_model().objects.create(comment='My Comment 2', site=site,
                                            content_object=self.relationtype)
        comments.get_model().objects.create(comment='My Comment 3', site=site,
                                            content_object=second_relationtype)
        context = get_popular_relationtypes(3)
        self.assertEquals(context['relationtypes'], [self.relationtype, second_relationtype])
        self.relationtype.status = DRAFT
        self.relationtype.save()
        context = get_popular_relationtypes(3)
        self.assertEquals(context['relationtypes'], [second_relationtype])

    def test_get_similar_relationtypes(self):
        self.publish_relationtype()
        source_context = Context({'object': self.relationtype})
        context = get_similar_relationtypes(source_context)
        self.assertEquals(len(context['relationtypes']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/similar_relationtypes.html')

        params = {'title': 'My second relationtype',
                  'content': 'This is the second relationtype of my tests.',
                  'tags': 'relationapp, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-relationtype'}
        site = Site.objects.get_current()
        second_relationtype = Relationtype.objects.create(**params)
        second_relationtype.sites.add(site)

        source_context = Context({'object': second_relationtype})
        context = get_similar_relationtypes(source_context, 3,
                                      'custom_template.html',
                                      flush=True)
        self.assertEquals(len(context['relationtypes']), 1)
        self.assertEquals(context['template'], 'custom_template.html')

    def test_get_archives_relationtypes(self):
        context = get_archives_relationtypes()
        self.assertEquals(len(context['archives']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/archives_relationtypes.html')

        self.publish_relationtype()
        params = {'title': 'My second relationtype',
                  'content': 'My second content',
                  'tags': 'relationapp, test',
                  'status': PUBLISHED,
                  'creation_date': datetime(2009, 1, 1),
                  'slug': 'my-second-relationtype'}
        site = Site.objects.get_current()
        second_relationtype = Relationtype.objects.create(**params)
        second_relationtype.sites.add(site)

        context = get_archives_relationtypes('custom_template.html')
        self.assertEquals(len(context['archives']), 2)
        self.assertEquals(context['archives'][0], datetime(2010, 1, 1))
        self.assertEquals(context['archives'][1], datetime(2009, 1, 1))
        self.assertEquals(context['template'], 'custom_template.html')

    def test_get_archives_tree(self):
        context = get_archives_relationtypes_tree()
        self.assertEquals(len(context['archives']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/archives_relationtypes_tree.html')

        self.publish_relationtype()
        params = {'title': 'My second relationtype',
                  'content': 'My second content',
                  'tags': 'relationapp, test',
                  'status': PUBLISHED,
                  'creation_date': datetime(2009, 1, 10),
                  'slug': 'my-second-relationtype'}
        site = Site.objects.get_current()
        second_relationtype = Relationtype.objects.create(**params)
        second_relationtype.sites.add(site)

        context = get_archives_relationtypes_tree('custom_template.html')
        self.assertEquals(len(context['archives']), 2)
        self.assertEquals(context['archives'][0], datetime(2009, 1, 10))
        self.assertEquals(context['archives'][1], datetime(2010, 1, 1))
        self.assertEquals(context['template'], 'custom_template.html')

    def test_get_calendar_relationtypes(self):
        source_context = Context()
        context = get_calendar_relationtypes(source_context)
        self.assertEquals(context['previous_month'], None)
        self.assertEquals(context['next_month'], None)
        self.assertEquals(context['template'], 'relationapp/tags/calendar.html')

        self.publish_relationtype()
        context = get_calendar_relationtypes(source_context,
                                       template='custom_template.html')
        self.assertEquals(context['previous_month'], datetime(2010, 1, 1))
        self.assertEquals(context['next_month'], None)
        self.assertEquals(context['template'], 'custom_template.html')

        context = get_calendar_relationtypes(source_context, 2009, 1)
        self.assertEquals(context['previous_month'], None)
        self.assertEquals(context['next_month'], datetime(2010, 1, 1))

        source_context = Context({'month': datetime(2009, 1, 1)})
        context = get_calendar_relationtypes(source_context)
        self.assertEquals(context['previous_month'], None)
        self.assertEquals(context['next_month'], datetime(2010, 1, 1))

        source_context = Context({'month': datetime(2010, 1, 1)})
        context = get_calendar_relationtypes(source_context)
        self.assertEquals(context['previous_month'], None)
        self.assertEquals(context['next_month'], None)

        params = {'title': 'My second relationtype',
                  'content': 'My second content',
                  'tags': 'relationapp, test',
                  'status': PUBLISHED,
                  'creation_date': datetime(2008, 1, 1),
                  'slug': 'my-second-relationtype'}
        site = Site.objects.get_current()
        second_relationtype = Relationtype.objects.create(**params)
        second_relationtype.sites.add(site)

        source_context = Context()
        context = get_calendar_relationtypes(source_context, 2009, 1)
        self.assertEquals(context['previous_month'], datetime(2008, 1, 1))
        self.assertEquals(context['next_month'], datetime(2010, 1, 1))
        context = get_calendar_relationtypes(source_context)
        self.assertEquals(context['previous_month'], datetime(2010, 1, 1))
        self.assertEquals(context['next_month'], None)

    def test_get_recent_comments(self):
        site = Site.objects.get_current()
        context = get_recent_comments()
        self.assertEquals(len(context['comments']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/recent_comments.html')

        comment_1 = comments.get_model().objects.create(
            comment='My Comment 1', site=site,
            content_object=self.relationtype)
        context = get_recent_comments(3, 'custom_template.html')
        self.assertEquals(len(context['comments']), 0)
        self.assertEquals(context['template'], 'custom_template.html')

        self.publish_relationtype()
        context = get_recent_comments()
        self.assertEquals(len(context['comments']), 1)

        author = User.objects.create_user(username='webmaster',
                                          email='webmaster@example.com')
        comment_2 = comments.get_model().objects.create(
            comment='My Comment 2', site=site,
            content_object=self.relationtype)
        comment_2.flags.create(user=author,
                               flag=CommentFlag.MODERATOR_APPROVAL)
        context = get_recent_comments()
        self.assertEquals(list(context['comments']), [comment_2, comment_1])

    def test_get_recent_linkbacks(self):
        user = User.objects.create_user(username='webmaster',
                                        email='webmaster@example.com')
        site = Site.objects.get_current()
        context = get_recent_linkbacks()
        self.assertEquals(len(context['linkbacks']), 0)
        self.assertEquals(context['template'],
                          'relationapp/tags/recent_linkbacks.html')

        linkback_1 = comments.get_model().objects.create(
            comment='My Linkback 1', site=site,
            content_object=self.relationtype)
        linkback_1.flags.create(user=user, flag='pingback')
        context = get_recent_linkbacks(3, 'custom_template.html')
        self.assertEquals(len(context['linkbacks']), 0)
        self.assertEquals(context['template'], 'custom_template.html')

        self.publish_relationtype()
        context = get_recent_linkbacks()
        self.assertEquals(len(context['linkbacks']), 1)

        linkback_2 = comments.get_model().objects.create(
            comment='My Linkback 2', site=site,
            content_object=self.relationtype)
        linkback_2.flags.create(user=user, flag='trackback')
        context = get_recent_linkbacks()
        self.assertEquals(list(context['linkbacks']), [linkback_2, linkback_1])

    def test_relationapp_pagination(self):
        class FakeRequest(object):
            def __init__(self, get_dict):
                self.GET = get_dict

        source_context = Context({'request': FakeRequest(
            {'page': '1', 'key': 'val'})})
        paginator = Paginator(range(200), 10)

        context = relationapp_pagination(source_context, paginator.page(1))
        self.assertEquals(context['page'].number, 1)
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [18, 19, 20])
        self.assertEquals(context['GET_string'], '&key=val')
        self.assertEquals(context['template'], 'relationapp/tags/pagination.html')

        source_context = Context({'request': FakeRequest({})})
        context = relationapp_pagination(source_context, paginator.page(2))
        self.assertEquals(context['page'].number, 2)
        self.assertEquals(context['begin'], [1, 2, 3, 4])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [18, 19, 20])
        self.assertEquals(context['GET_string'], '')

        context = relationapp_pagination(source_context, paginator.page(3))
        self.assertEquals(context['begin'], [1, 2, 3, 4, 5])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(6))
        self.assertEquals(context['begin'], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(11))
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [9, 10, 11, 12, 13])
        self.assertEquals(context['end'], [18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(15))
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [13, 14, 15, 16, 17, 18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(18))
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [16, 17, 18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(19))
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [17, 18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(20))
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [18, 19, 20])

        context = relationapp_pagination(source_context, paginator.page(10),
                                    begin_pages=1, end_pages=3,
                                    before_pages=4, after_pages=3,
                                    template='custom_template.html')
        self.assertEquals(context['begin'], [1])
        self.assertEquals(context['middle'], [6, 7, 8, 9, 10, 11, 12, 13])
        self.assertEquals(context['end'], [18, 19, 20])
        self.assertEquals(context['template'], 'custom_template.html')

        paginator = Paginator(range(50), 10)
        context = relationapp_pagination(source_context, paginator.page(1))
        self.assertEquals(context['begin'], [1, 2, 3, 4, 5])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [])

        paginator = Paginator(range(60), 10)
        context = relationapp_pagination(source_context, paginator.page(1))
        self.assertEquals(context['begin'], [1, 2, 3, 4, 5, 6])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [])

        paginator = Paginator(range(70), 10)
        context = relationapp_pagination(source_context, paginator.page(1))
        self.assertEquals(context['begin'], [1, 2, 3])
        self.assertEquals(context['middle'], [])
        self.assertEquals(context['end'], [5, 6, 7])

    def test_relationapp_breadcrumbs(self):
        class FakeRequest(object):
            def __init__(self, path):
                self.path = path

        source_context = Context({'request': FakeRequest('/')})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 1)
        self.assertEquals(context['breadcrumbs'][0].name, 'Blog')
        self.assertEquals(context['breadcrumbs'][0].url,
                          reverse('relationapp_relationtype_archive_index'))
        self.assertEquals(context['separator'], '/')
        self.assertEquals(context['template'], 'relationapp/tags/breadcrumbs.html')

        context = relationapp_breadcrumbs(source_context,
                                     '>', 'Weblog', 'custom_template.html')
        self.assertEquals(len(context['breadcrumbs']), 1)
        self.assertEquals(context['breadcrumbs'][0].name, 'Weblog')
        self.assertEquals(context['separator'], '>')
        self.assertEquals(context['template'], 'custom_template.html')

        source_context = Context(
            {'request': FakeRequest(self.relationtype.get_absolute_url()),
             'object': self.relationtype})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 5)

        cat_1 = Relation.objects.create(title='Relation 1', slug='relation-1')
        source_context = Context(
            {'request': FakeRequest(cat_1.get_absolute_url()),
             'object': cat_1})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 3)
        cat_2 = Relation.objects.create(title='Relation 2', slug='relation-2',
                                        parent=cat_1)
        source_context = Context(
            {'request': FakeRequest(cat_2.get_absolute_url()),
             'object': cat_2})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 4)

        tag = Tag.objects.get(name='test')
        source_context = Context(
            {'request': FakeRequest(reverse('relationapp_tag_detail',
                                            args=['test'])),
             'object': tag})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 3)

        User.objects.create_user(username='webmaster',
                                 email='webmaster@example.com')
        author = Author.objects.get(username='webmaster')
        source_context = Context(
            {'request': FakeRequest(author.get_absolute_url()),
             'object': author})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 3)

        source_context = Context(
            {'request': FakeRequest(reverse(
                'relationapp_relationtype_archive_year', args=[2011]))})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 2)

        source_context = Context({'request': FakeRequest(reverse(
            'relationapp_relationtype_archive_month', args=[2011, '03']))})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 3)

        source_context = Context({'request': FakeRequest(reverse(
            'relationapp_relationtype_archive_day', args=[2011, '03', 15]))})
        context = relationapp_breadcrumbs(source_context)
        self.assertEquals(len(context['breadcrumbs']), 4)
        # More tests can be done here, for testing path and objects in context

    def test_get_gravatar(self):
        self.assertEquals(
            get_gravatar('webmaster@example.com'),
            'http://www.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592.jpg?s=80&amp;r=g')
        self.assertEquals(
            get_gravatar('  WEBMASTER@example.com  ', 15, 'x', '404'),
            'http://www.gravatar.com/avatar/86d4fd4a22de452'
            'a9228298731a0b592.jpg?s=15&amp;r=x&amp;d=404')

    def test_get_tags(self):
        Tag.objects.create(name='tag')
        t = Template("""
        {% load relationapp_tags %}
        {% get_tags as relationtype_tags %}
        {{ relationtype_tags|join:", " }}
        """)
        html = t.render(Context())
        self.assertEquals(html.strip(), '')
        self.publish_relationtype()
        html = t.render(Context())
        self.assertEquals(html.strip(), 'test, relationapp')

        template_error_as = """
        {% load relationapp_tags %}
        {% get_tags a_s relationtype_tags %}"""
        self.assertRaises(TemplateSyntaxError, Template, template_error_as)

        template_error_args = """
        {% load relationapp_tags %}
        {% get_tags as relationtype tags %}"""
        self.assertRaises(TemplateSyntaxError, Template, template_error_args)

    def test_get_tag_cloud(self):
        context = get_tag_cloud()
        self.assertEquals(len(context['tags']), 0)
        self.assertEquals(context['template'], 'relationapp/tags/tag_cloud.html')
        self.publish_relationtype()
        context = get_tag_cloud(6, 'custom_template.html')
        self.assertEquals(len(context['tags']), 2)
        self.assertEquals(context['template'], 'custom_template.html')
