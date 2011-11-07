"""Test cases for Gstudio's views"""
from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist
from django.utils.translation import ugettext_lazy as _

from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.managers import PUBLISHED
from gstudio.settings import PAGINATION


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
        self.metatype = Metatype.objects.create(title='Tests', slug='tests')
        params = {'title': 'Test 1',
                  'content': 'First test objecttype published',
                  'slug': 'test-1',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        objecttype = Objecttype.objects.create(**params)
        objecttype.sites.add(self.site)
        objecttype.metatypes.add(self.metatype)
        objecttype.authors.add(self.author)

        params = {'title': 'Test 2',
                  'content': 'Second test objecttype published',
                  'slug': 'test-2',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 6, 1),
                  'status': PUBLISHED}
        objecttype = Objecttype.objects.create(**params)
        objecttype.sites.add(self.site)
        objecttype.metatypes.add(self.metatype)
        objecttype.authors.add(self.author)

    def tearDown(self):
        settings.TEMPLATE_CONTEXT_PROCESSORS = self.old_CONTEXT_PROCESSORS
        settings.TEMPLATE_LOADERS = self.old_TEMPLATE_LOADERS

    def create_published_objecttype(self):
        params = {'title': 'My test objecttype',
                  'content': 'My test content',
                  'slug': 'my-test-objecttype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        objecttype = Objecttype.objects.create(**params)
        objecttype.sites.add(self.site)
        objecttype.metatypes.add(self.metatype)
        objecttype.authors.add(self.author)
        return objecttype

    def check_publishing_context(self, url, first_expected,
                                 second_expected=None):
        """Test the numbers of objecttypes in context of an url,"""
        response = self.client.get(url)
        self.assertEquals(len(response.context['object_list']), first_expected)
        if second_expected:
            self.create_published_objecttype()
            response = self.client.get(url)
            self.assertEquals(
                len(response.context['object_list']), second_expected)
        return response


class GstudioViewsTestCase(ViewsBaseCase):
    """
    Test cases for generic views used in the application,
    for reproducing and correcting issue :
    http://github.com/gnowgi/django-gstudio/issues#issue/3
    """
    urls = 'gstudio.tests.urls'

    def test_gstudio_objecttype_archive_index(self):
        self.check_publishing_context('/', 2, 3)

    def test_gstudio_objecttype_archive_year(self):
        self.check_publishing_context('/2010/', 2, 3)

    def test_gstudio_objecttype_archive_month(self):
        self.check_publishing_context('/2010/01/', 1, 2)

    def test_gstudio_objecttype_archive_day(self):
        self.check_publishing_context('/2010/01/01/', 1, 2)

    def test_gstudio_objecttype_shortlink(self):
        response = self.client.get('/1/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/2010/01/01/test-1/', 301)])

    def test_gstudio_objecttype_detail(self):
        objecttype = self.create_published_objecttype()
        objecttype.sites.clear()
        # Check a 404 error, but the 404.html may no exist
        try:
            self.assertRaises(TemplateDoesNotExist, self.client.get,
                              '/2010/01/01/my-test-objecttype/')
        except AssertionError:
            response = self.client.get('/2010/01/01/my-test-objecttype/')
            self.assertEquals(response.status_code, 404)

        objecttype.template = 'gstudio/_objecttype_detail.html'
        objecttype.save()
        objecttype.sites.add(Site.objects.get_current())
        response = self.client.get('/2010/01/01/my-test-objecttype/')
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'gstudio/_objecttype_detail.html')

    def test_gstudio_objecttype_detail_login(self):
        objecttype = self.create_published_objecttype()
        objecttype.login_required = True
        objecttype.save()
        response = self.client.get('/2010/01/01/my-test-objecttype/')
        self.assertTemplateUsed(response, 'gstudio/login.html')

    def test_gstudio_objecttype_detail_password(self):
        objecttype = self.create_published_objecttype()
        objecttype.password = 'password'
        objecttype.save()
        response = self.client.get('/2010/01/01/my-test-objecttype/')
        self.assertTemplateUsed(response, 'gstudio/password.html')
        self.assertEquals(response.context['error'], False)
        response = self.client.post('/2010/01/01/my-test-objecttype/',
                                    {'password': 'bad_password'})
        self.assertTemplateUsed(response, 'gstudio/password.html')
        self.assertEquals(response.context['error'], True)
        response = self.client.post('/2010/01/01/my-test-objecttype/',
                                    {'password': 'password'})
        self.assertEquals(response.status_code, 302)

    def test_gstudio_objecttype_channel(self):
        self.check_publishing_context('/channel-test/', 2, 3)

    def test_gstudio_metatype_list(self):
        self.check_publishing_context('/metatypes/', 1)
        objecttype = Objecttype.objects.all()[0]
        objecttype.metatypes.add(Metatype.objects.create(title='New metatype',
                                                     slug='new-metatype'))
        self.check_publishing_context('/metatypes/', 2)

    def test_gstudio_metatype_detail(self):
        response = self.check_publishing_context('/metatypes/tests/', 2, 3)
        self.assertTemplateUsed(response, 'gstudio/metatype/objecttype_list.html')
        self.assertEquals(response.context['metatype'].slug, 'tests')

    def test_gstudio_metatype_detail_paginated(self):
        """Test case reproducing issue #42 on metatype
        detail view paginated"""
        for i in range(PAGINATION):
            params = {'title': 'My objecttype %i' % i,
                      'content': 'My content %i' % i,
                      'slug': 'my-objecttype-%i' % i,
                      'creation_date': datetime(2010, 1, 1),
                      'status': PUBLISHED}
            objecttype = Objecttype.objects.create(**params)
            objecttype.sites.add(self.site)
            objecttype.metatypes.add(self.metatype)
            objecttype.authors.add(self.author)
        response = self.client.get('/metatypes/tests/')
        self.assertEquals(len(response.context['object_list']), PAGINATION)
        response = self.client.get('/metatypes/tests/?page=2')
        self.assertEquals(len(response.context['object_list']), 2)
        response = self.client.get('/metatypes/tests/page/2/')
        self.assertEquals(len(response.context['object_list']), 2)
        self.assertEquals(response.context['metatype'].slug, 'tests')

    def test_gstudio_author_list(self):
        self.check_publishing_context('/authors/', 1)
        objecttype = Objecttype.objects.all()[0]
        objecttype.authors.add(User.objects.create(username='new-user',
                                              email='new_user@example.com'))
        self.check_publishing_context('/authors/', 2)

    def test_gstudio_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'gstudio/author/objecttype_list.html')
        self.assertEquals(response.context['author'].username, 'admin')

    def test_gstudio_tag_list(self):
        self.check_publishing_context('/tags/', 1)
        objecttype = Objecttype.objects.all()[0]
        objecttype.tags = 'tests, tag'
        objecttype.save()
        self.check_publishing_context('/tags/', 2)

    def test_gstudio_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'gstudio/tag/objecttype_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')

    def test_gstudio_objecttype_search(self):
        self.check_publishing_context('/search/?pattern=test', 2, 3)
        response = self.client.get('/search/?pattern=ab')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('The pattern is too short'))
        response = self.client.get('/search/')
        self.assertEquals(len(response.context['object_list']), 0)
        self.assertEquals(response.context['error'],
                          _('No pattern to search found'))

    def test_gstudio_sitemap(self):
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['objecttypes']), 2)
        self.assertEquals(len(response.context['metatypes']), 1)
        objecttype = self.create_published_objecttype()
        objecttype.metatypes.add(Metatype.objects.create(title='New metatype',
                                                     slug='new-metatype'))
        response = self.client.get('/sitemap/')
        self.assertEquals(len(response.context['objecttypes']), 3)
        self.assertEquals(len(response.context['metatypes']), 2)

    def test_gstudio_trackback(self):
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
        objecttype = Objecttype.objects.get(slug='test-1')
        objecttype.pingback_enabled = False
        objecttype.save()
        self.assertEquals(
            self.client.post('/trackback/1/',
                             {'url': 'http://example.com'}).content,
            '<?xml version="1.0" encoding="utf-8"?>\n<response>\n  \n  '
            '<error>1</error>\n  <message>Trackback is not enabled for '
            'Test 1</message>\n  \n</response>\n')
        objecttype.pingback_enabled = True
        objecttype.save()
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


class GstudioCustomDetailViews(ViewsBaseCase):
    """
    Tests with an alternate urls.py that modifies how author_detail,
    tags_detail and metatypes_detail views to be called with a custom
    template_name keyword argument and an extra_context.
    """
    urls = 'gstudio.tests.custom_views_detail_urls'

    def test_custom_metatype_detail(self):
        response = self.check_publishing_context('/metatypes/tests/', 2, 3)
        self.assertTemplateUsed(response, 'gstudio/objecttype_list.html')
        self.assertEquals(response.context['metatype'].slug, 'tests')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_author_detail(self):
        response = self.check_publishing_context('/authors/admin/', 2, 3)
        self.assertTemplateUsed(response, 'gstudio/objecttype_list.html')
        self.assertEquals(response.context['author'].username, 'admin')
        self.assertEquals(response.context['extra'], 'context')

    def test_custom_tag_detail(self):
        response = self.check_publishing_context('/tags/tests/', 2, 3)
        self.assertTemplateUsed(response, 'gstudio/objecttype_list.html')
        self.assertEquals(response.context['tag'].name, 'tests')
        self.assertEquals(response.context['extra'], 'context')
