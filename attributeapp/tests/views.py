"""Test cases for Attributeapp's views"""
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.managers import PUBLISHED
from attributeapp.settings import PAGINATION


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
        self.attribute = Attribute.objects.create(title='Tests', slug='tests')
        params = {'title': 'Test 1',
                  'content': 'First test attributetype published',
                  'slug': 'test-1',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        attributetype = Attributetype.objects.create(**params)
        attributetype.sites.add(self.site)
        attributetype.attributes.add(self.attribute)
        attributetype.authors.add(self.author)

        params = {'title': 'Test 2',
                  'content': 'Second test attributetype published',
                  'slug': 'test-2',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 6, 1),
                  'status': PUBLISHED}
        attributetype = Attributetype.objects.create(**params)
        attributetype.sites.add(self.site)
        attributetype.attributes.add(self.attribute)
        attributetype.authors.add(self.author)

    def tearDown(self):
        settings.TEMPLATE_CONTEXT_PROCESSORS = self.old_CONTEXT_PROCESSORS
        settings.TEMPLATE_LOADERS = self.old_TEMPLATE_LOADERS

    def create_published_attributetype(self):
        params = {'title': 'My test attributetype',
                  'content': 'My test content',
                  'slug': 'my-test-attributetype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        attributetype = Attributetype.objects.create(**params)
        attributetype.sites.add(self.site)
        attributetype.attributes.add(self.attribute)
        attributetype.authors.add(self.author)
        return attributetype

    def check_publishing_context(self, url, first_expected,
                                 second_expected=None):
        """Test the numbers of attributetypes in context of an url,"""
        response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']), first_expected)
        if second_expected:
            self.create_published_attributetype()
            response = self.client.get(url)
            self.assertEquals(
                len(response.context['object_list']), second_expected)
        return response


class AttributeappViewsTestCase(ViewsBaseCase):
    """
    Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/gnowgi/django-attributeapp/issues#issue/3
    """
    urls = 'attributeapp.tests.urls'

    def test_attributeapp_attributetype_archive_index(self):
        self.check_publishing_context('/', 2, 3)

    def test_attributeapp_attributetype_archive_year(self):
        self.check_publishing_context('/2010/', 2, 3)

    def test_attributeapp_attributetype_archive_month(self):
        self.check_publishing_context('/2010/01/', 1, 2)

    def test_attributeapp_attributetype_archive_day(self):
        self.check_publishing_context('/2010/01/01/', 1, 2)

    def test_attributeapp_attributetype_shortlink(self):
        response = self.client.get('/1/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/2010/01/01/test-1/', 301)])

    def test_attributeapp_attributetype_detail(self):
        attributetype = self.create_published_attributetype()
        attributetype.sites.clear()
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.get,
                              '/2010/01/01/my-test-attributetype/')
        except AssertionError:
            response = self.client.get('/2010/01/01/my-test-attributetype/')
            self.assertEquals(response.status_code, 404)

        attributetype.template = 'attributeapp/_attributetype_detail.html'
        attributetype.save()
        attributetype.sites.add(Site.objects.get_current())
        response = self.client.get('/2010/01/01/my-test-attributetype/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'attributeapp/_attributetype_detail.html')

    def test_attributeapp_attributetype_detail_login(self):
        attributetype = self.create_published_attributetype()
        attributetype.login_required = True
        attributetype.save()
        response = self.client.get('/2010/01/01/my-test-attributetype/')
        self.assertTemplateUsed(response, 'attributeapp/login.html')

    def test_attributeapp_attributetype_detail_password(self):
        attributetype = self.create_published_attributetype()
        attributetype.password = 'password'
        attributetype.save()
        response = self.client.get('/2010/01/01/my-test-attributetype/')
        self.assertTemplateUsed(response, 'attributeapp/password.html')
        self.assertEquals(response.context['error'], False)
        response = self.client.post('/2010/01/01/my-test-attributetype/',
                                    {'password': 'bad_password'})
        self.assertTemplateUsed(response, 'attributeapp/password.html')
        self.assertEquals(response.context['error'], True)
        response = self.client.post('/2010/01/01/my-test-attributetype/',
                                    {'password': 'password'})
        self.assertEquals(response.status_code, 302)

    def test_attributeapp_attributetype_channel(self):
        self.check_publishing_context('/channel-test/', 2, 3)

    def test_attributeapp_attribute_list(self):
        self.check_publishing_context('/attributes/', 1)
        attributetype = Attributetype.objects.all()[0]
        attributetype.attributes.add(Attribute.objects.create(title='New attribute',
                                                     slug='new-attribute'))
        self.check_publishing_context('/attributes/', 2)

    def test_attributeapp_attribute_detail(self):
        response = self.check_publishing_context('/attributes/tests/', 2, 3)
        self.assertTemplateUsed(response, 'attributeapp/attribute/attributetype_list.html')
        self.assertEquals(response.context['attribute'].slug, 'tests')

    def test_attributeapp_attribute_detail_paginated(self):
        """Test case reproducing issue #42 on attribute
        detail view paginated"""
        for i in range(PAGINATION):
            params = {'title': 'My attributetype %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-attributetype-%i' % i,
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            attributetype = Attributetype.objects.create(**params)
            attributetype.sites.add(self.site)
            attributetype.attributes.add(self.attribute)
            attributetype.authors.add(self.author)
        response = self.client.get('/attributes/tests/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/attributes/tests/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/attributes/tests/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['attribute'].slug, 'tests')

    def test_attributeapp_author_list(self):
        self.check_publishing_context('/authors/', 1)
        attributetype = Attributetype.objects.all()[0]
        attributetype.authors.add(User.objects.create(username='new-user',
                                              email='new_user@example.com'))
        self.check_publishing_context('/authors/', 2)

    def test_attributeapp_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'attributeapp/author/attributetype_list.html')
        self.assertEquals(response.context['author'].username, 'admin')

    def test_attributeapp_tag_list(self):
        self.check_publishing_context('/tags/', 1)
        attributetype = Attributetype.objects.all()[0]
        attributetype.tags = 'tests, tag'
        attributetype.save()
        self.check_publishing_context('/tags/', 2)

    def test_attributeapp_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'attributeapp/tag/attributetype_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')

    def test_attributeapp_attributetype_search(self):
        self.check_publishing_context('/search/?pattern=test', 2, 3)
        response = self.client.get('/search/?pattern=ab')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('No pattern to search found'))

    def test_attributeapp_sitemap(self):
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['attributetypes']), 2)
        self.assertEquals(len(response.context['attributes']), 1)
        attributetype = self.create_published_attributetype()
        attributetype.attributes.add(Attribute.objects.create(title='New attribute',
                                                     slug='new-attribute'))
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['attributetypes']), 3)
        self.assertEquals(len(response.context['attributes']), 2)

    def test_attributeapp_trackback(self):
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
        attributetype = Attributetype.objects.get(slug='test-1')
        attributetype.pingback_enabled = False
        attributetype.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is not enabled for '
            'Test 1</message>\n  \n</response>\n')
        attributetype.pingback_enabled = True
        attributetype.save()
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


class AttributeappCustomDetailViews(ViewsBaseCase):
    """
    Tests with an alternate urls.py that modifies how author_detail,
    tags_detail and attributes_detail views to be called with a custom
    template_name keyword argument and an extra_context.
    """
    urls = 'attributeapp.tests.custom_views_detail_urls'

    def test_custom_attribute_detail(self):
        response = self.check_publishing_context('/attributes/tests/', 2, 3)
        self.assertTemplateUsed(response, 'attributeapp/attributetype_list.html')
        self.assertEquals(response.context['attribute'].slug, 'tests')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'attributeapp/attributetype_list.html')
        self.assertEquals(response.context['author'].username, 'admin')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'attributeapp/attributetype_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        self.assertEquals(response.context['extra'], 'context')
