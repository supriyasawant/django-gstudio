"""Test cases for Relationapp's views"""
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.managers import PUBLISHED
from relationapp.settings import PAGINATION


class ViewsBaseCase(TestCase):
    """
    Setup and utility function base case.
    """

    def setUp(self):
        self.old_CONTEXT_PROCESSORS = settings.TEMPLATE_CONTEXT_PROCESSORS
        self.old_TEMPLATE_LOADERS = settings.TEMPLATE_LOADERS
        settings.TEMPLATE_LOADERS = (
            ('django.template.loaders.cached.Loader', (
                'django.template.loaders.app_directories.Loader',
                'django.template.loaders.eggs.Loader',
                )
             ),
            )
        settings.TEMPLATE_CONTEXT_PROCESSORS = (
            'django.core.context_processors.request',
            )

        self.site = Site.objects.get_current()
        self.author = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='password')
        self.relation = Relation.objects.create(title='Tests', slug='tests')
        params = {'title': 'Test 1',
                  'content': 'First test relationtype published',
                  'slug': 'test-1',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        relationtype = Relationtype.objects.create(**params)
        relationtype.sites.add(self.site)
        relationtype.relations.add(self.relation)
        relationtype.authors.add(self.author)

        params = {'title': 'Test 2',
                  'content': 'Second test relationtype published',
                  'slug': 'test-2',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 6, 1),
                  'status': PUBLISHED}
        relationtype = Relationtype.objects.create(**params)
        relationtype.sites.add(self.site)
        relationtype.relations.add(self.relation)
        relationtype.authors.add(self.author)

    def tearDown(self):
        settings.TEMPLATE_CONTEXT_PROCESSORS = self.old_CONTEXT_PROCESSORS
        settings.TEMPLATE_LOADERS = self.old_TEMPLATE_LOADERS

    def create_published_relationtype(self):
        params = {'title': 'My test relationtype',
                  'content': 'My test content',
                  'slug': 'my-test-relationtype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        relationtype = Relationtype.objects.create(**params)
        relationtype.sites.add(self.site)
        relationtype.relations.add(self.relation)
        relationtype.authors.add(self.author)
        return relationtype

    def check_publishing_context(self, url, first_expected,
                                 second_expected=None):
        """Test the numbers of relationtypes in context of an url,"""
        response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']), first_expected)
        if second_expected:
            self.create_published_relationtype()
            response = self.client.get(url)
            self.assertEquals(
                len(response.context['object_list']), second_expected)
        return response


class RelationappViewsTestCase(ViewsBaseCase):
    """
    Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/gnowgi/django-relationapp/issues#issue/3
    """
    urls = 'relationapp.tests.urls'

    def test_relationapp_relationtype_archive_index(self):
        self.check_publishing_context('/', 2, 3)

    def test_relationapp_relationtype_archive_year(self):
        self.check_publishing_context('/2010/', 2, 3)

    def test_relationapp_relationtype_archive_month(self):
        self.check_publishing_context('/2010/01/', 1, 2)

    def test_relationapp_relationtype_archive_day(self):
        self.check_publishing_context('/2010/01/01/', 1, 2)

    def test_relationapp_relationtype_shortlink(self):
        response = self.client.get('/1/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/2010/01/01/test-1/', 301)])

    def test_relationapp_relationtype_detail(self):
        relationtype = self.create_published_relationtype()
        relationtype.sites.clear()
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.get,
                              '/2010/01/01/my-test-relationtype/')
        except AssertionError:
            response = self.client.get('/2010/01/01/my-test-relationtype/')
            self.assertEquals(response.status_code, 404)

        relationtype.template = 'relationapp/_relationtype_detail.html'
        relationtype.save()
        relationtype.sites.add(Site.objects.get_current())
        response = self.client.get('/2010/01/01/my-test-relationtype/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'relationapp/_relationtype_detail.html')

    def test_relationapp_relationtype_detail_login(self):
        relationtype = self.create_published_relationtype()
        relationtype.login_required = True
        relationtype.save()
        response = self.client.get('/2010/01/01/my-test-relationtype/')
        self.assertTemplateUsed(response, 'relationapp/login.html')

    def test_relationapp_relationtype_detail_password(self):
        relationtype = self.create_published_relationtype()
        relationtype.password = 'password'
        relationtype.save()
        response = self.client.get('/2010/01/01/my-test-relationtype/')
        self.assertTemplateUsed(response, 'relationapp/password.html')
        self.assertEquals(response.context['error'], False)
        response = self.client.post('/2010/01/01/my-test-relationtype/',
                                    {'password': 'bad_password'})
        self.assertTemplateUsed(response, 'relationapp/password.html')
        self.assertEquals(response.context['error'], True)
        response = self.client.post('/2010/01/01/my-test-relationtype/',
                                    {'password': 'password'})
        self.assertEquals(response.status_code, 302)

    def test_relationapp_relationtype_channel(self):
        self.check_publishing_context('/channel-test/', 2, 3)

    def test_relationapp_relation_list(self):
        self.check_publishing_context('/relations/', 1)
        relationtype = Relationtype.objects.all()[0]
        relationtype.relations.add(Relation.objects.create(title='New relation',
                                                     slug='new-relation'))
        self.check_publishing_context('/relations/', 2)

    def test_relationapp_relation_detail(self):
        response = self.check_publishing_context('/relations/tests/', 2, 3)
        self.assertTemplateUsed(response, 'relationapp/relation/relationtype_list.html')
        self.assertEquals(response.context['relation'].slug, 'tests')

    def test_relationapp_relation_detail_paginated(self):
        """Test case reproducing issue #42 on relation
        detail view paginated"""
        for i in range(PAGINATION):
            params = {'title': 'My relationtype %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-relationtype-%i' % i,
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            relationtype = Relationtype.objects.create(**params)
            relationtype.sites.add(self.site)
            relationtype.relations.add(self.relation)
            relationtype.authors.add(self.author)
        response = self.client.get('/relations/tests/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/relations/tests/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/relations/tests/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['relation'].slug, 'tests')

    def test_relationapp_author_list(self):
        self.check_publishing_context('/authors/', 1)
        relationtype = Relationtype.objects.all()[0]
        relationtype.authors.add(User.objects.create(username='new-user',
                                              email='new_user@example.com'))
        self.check_publishing_context('/authors/', 2)

    def test_relationapp_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'relationapp/author/relationtype_list.html')
        self.assertEquals(response.context['author'].username, 'admin')

    def test_relationapp_tag_list(self):
        self.check_publishing_context('/tags/', 1)
        relationtype = Relationtype.objects.all()[0]
        relationtype.tags = 'tests, tag'
        relationtype.save()
        self.check_publishing_context('/tags/', 2)

    def test_relationapp_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'relationapp/tag/relationtype_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')

    def test_relationapp_relationtype_search(self):
        self.check_publishing_context('/search/?pattern=test', 2, 3)
        response = self.client.get('/search/?pattern=ab')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('No pattern to search found'))

    def test_relationapp_sitemap(self):
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['relationtypes']), 2)
        self.assertEquals(len(response.context['relations']), 1)
        relationtype = self.create_published_relationtype()
        relationtype.relations.add(Relation.objects.create(title='New relation',
                                                     slug='new-relation'))
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['relationtypes']), 3)
        self.assertEquals(len(response.context['relations']), 2)

    def test_relationapp_trackback(self):
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.post,
                              '/trackback/404/')
        except AssertionError:
            response = self.client.post('/trackback/404/')
            self.assertEquals(response.status_code, 404)
        self.assertEquals(
            self.client.post('/trackback/1/').status_code, 301)
        self.assertEquals(
            self.client.get('/trackback/1/').status_code, 301)
        relationtype = Relationtype.objects.get(slug='test-1')
        relationtype.pingback_enabled = False
        relationtype.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is not enabled for '
            'Test 1</message>\n  \n</response>\n')
        relationtype.pingback_enabled = True
        relationtype.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>0</error>\n  \n</response>\n')
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is already registered'
            '</message>\n  \n</response>\n')


class RelationappCustomDetailViews(ViewsBaseCase):
    """
    Tests with an alternate urls.py that modifies how author_detail,
    tags_detail and relations_detail views to be called with a custom
    template_name keyword argument and an extra_context.
    """
    urls = 'relationapp.tests.custom_views_detail_urls'

    def test_custom_relation_detail(self):
        response = self.check_publishing_context('/relations/tests/', 2, 3)
        self.assertTemplateUsed(response, 'relationapp/relationtype_list.html')
        self.assertEquals(response.context['relation'].slug, 'tests')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'relationapp/relationtype_list.html')
        self.assertEquals(response.context['author'].username, 'admin')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'relationapp/relationtype_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        self.assertEquals(response.context['extra'], 'context')
