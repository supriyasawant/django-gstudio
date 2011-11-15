"""Test cases for Attributeapp's Attributetype"""
from __future__ import with_statement
import warnings
from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.conf import settings
from django.contrib import comments
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.contrib.comments.models import CommentFlag

from attributeapp import models
from attributeapp.models import Attributetype
from attributeapp.managers import PUBLISHED
from attributeapp.models import get_base_model
from attributeapp.models import Attributetype
from attributeapp import models as models_settings
from attributeapp import url_shortener as shortener_settings


class AttributetypeTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My attributetype',
                  'content': 'My content',
                  'slug': 'my-attributetype'}
        self.attributetype = Attributetype.objects.create(**params)

    def test_discussions(self):
        site = Site.objects.get_current()
        self.assertEquals(self.attributetype.discussions.count(), 0)
        self.assertEquals(self.attributetype.comments.count(), 0)
        self.assertEquals(self.attributetype.pingbacks.count(), 0)
        self.assertEquals(self.attributetype.trackbacks.count(), 0)

        comments.get_model().objects.create(comment='My Comment 1',
                                            content_object=self.attributetype,
                                            site=site)
        self.assertEquals(self.attributetype.discussions.count(), 1)
        self.assertEquals(self.attributetype.comments.count(), 1)
        self.assertEquals(self.attributetype.pingbacks.count(), 0)
        self.assertEquals(self.attributetype.trackbacks.count(), 0)

        comments.get_model().objects.create(comment='My Comment 2',
                                            content_object=self.attributetype,
                                            site=site, is_public=False)
        self.assertEquals(self.attributetype.discussions.count(), 1)
        self.assertEquals(self.attributetype.comments.count(), 1)
        self.assertEquals(self.attributetype.pingbacks.count(), 0)
        self.assertEquals(self.attributetype.trackbacks.count(), 0)

        author = User.objects.create_user(username='webmaster',
                                          email='webmaster@example.com')

        comment = comments.get_model().objects.create(
            comment='My Comment 3',
            content_object=self.attributetype,
            site=Site.objects.create(domain='http://toto.com',
                                     name='Toto.com'))
        comment.flags.create(user=author, flag=CommentFlag.MODERATOR_APPROVAL)
        self.assertEquals(self.attributetype.discussions.count(), 2)
        self.assertEquals(self.attributetype.comments.count(), 2)
        self.assertEquals(self.attributetype.pingbacks.count(), 0)
        self.assertEquals(self.attributetype.trackbacks.count(), 0)

        comment = comments.get_model().objects.create(
            comment='My Pingback 1', content_object=self.attributetype, site=site)
        comment.flags.create(user=author, flag='pingback')
        self.assertEquals(self.attributetype.discussions.count(), 3)
        self.assertEquals(self.attributetype.comments.count(), 2)
        self.assertEquals(self.attributetype.pingbacks.count(), 1)
        self.assertEquals(self.attributetype.trackbacks.count(), 0)

        comment = comments.get_model().objects.create(
            comment='My Trackback 1', content_object=self.attributetype, site=site)
        comment.flags.create(user=author, flag='trackback')
        self.assertEquals(self.attributetype.discussions.count(), 4)
        self.assertEquals(self.attributetype.comments.count(), 2)
        self.assertEquals(self.attributetype.pingbacks.count(), 1)
        self.assertEquals(self.attributetype.trackbacks.count(), 1)

    def test_str(self):
        self.assertEquals(str(self.attributetype), 'My attributetype: draft')

    def test_word_count(self):
        self.assertEquals(self.attributetype.word_count, 2)

    def test_comments_are_open(self):
        original_auto_close = models.AUTO_CLOSE_COMMENTS_AFTER
        models.AUTO_CLOSE_COMMENTS_AFTER = None
        self.assertEquals(self.attributetype.comments_are_open, True)
        models.AUTO_CLOSE_COMMENTS_AFTER = 5
        self.attributetype.start_publication = datetime.now() - timedelta(days=7)
        self.attributetype.save()
        self.assertEquals(self.attributetype.comments_are_open, False)

        models.AUTO_CLOSE_COMMENTS_AFTER = original_auto_close

    def test_is_actual(self):
        self.assertTrue(self.attributetype.is_actual)
        self.attributetype.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.attributetype.is_actual)
        self.attributetype.start_publication = datetime.now()
        self.assertTrue(self.attributetype.is_actual)
        self.attributetype.end_publication = datetime(2000, 3, 15)
        self.assertFalse(self.attributetype.is_actual)

    def test_is_visible(self):
        self.assertFalse(self.attributetype.is_visible)
        self.attributetype.status = PUBLISHED
        self.assertTrue(self.attributetype.is_visible)
        self.attributetype.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.attributetype.is_visible)

    def test_short_url(self):
        original_shortener = shortener_settings.URL_SHORTENER_BACKEND
        shortener_settings.URL_SHORTENER_BACKEND = 'attributeapp.url_shortener.'\
                                                   'backends.default'
        self.assertEquals(self.attributetype.short_url,
                          'http://example.com' +
                          reverse('attributeapp_attributetype_shortlink',
                                  args=[self.attributetype.pk]))
        shortener_settings.URL_SHORTENER_BACKEND = original_shortener

    def test_previous_attributetype(self):
        site = Site.objects.get_current()
        self.assertFalse(self.attributetype.previous_attributetype)
        params = {'title': 'My second attributetype',
                  'content': 'My second content',
                  'slug': 'my-second-attributetype',
                  'creation_date': datetime(2000, 1, 1),
                  'status': PUBLISHED}
        self.second_attributetype = Attributetype.objects.create(**params)
        self.second_attributetype.sites.add(site)
        self.assertEquals(self.attributetype.previous_attributetype, self.second_attributetype)
        params = {'title': 'My third attributetype',
                  'content': 'My third content',
                  'slug': 'my-third-attributetype',
                  'creation_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.third_attributetype = Attributetype.objects.create(**params)
        self.third_attributetype.sites.add(site)
        self.assertEquals(self.attributetype.previous_attributetype, self.third_attributetype)
        self.assertEquals(self.third_attributetype.previous_attributetype, self.second_attributetype)

    def test_next_attributetype(self):
        site = Site.objects.get_current()
        self.assertFalse(self.attributetype.next_attributetype)
        params = {'title': 'My second attributetype',
                  'content': 'My second content',
                  'slug': 'my-second-attributetype',
                  'creation_date': datetime(2100, 1, 1),
                  'status': PUBLISHED}
        self.second_attributetype = Attributetype.objects.create(**params)
        self.second_attributetype.sites.add(site)
        self.assertEquals(self.attributetype.next_attributetype, self.second_attributetype)
        params = {'title': 'My third attributetype',
                  'content': 'My third content',
                  'slug': 'my-third-attributetype',
                  'creation_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_attributetype = Attributetype.objects.create(**params)
        self.third_attributetype.sites.add(site)
        self.assertEquals(self.attributetype.next_attributetype, self.third_attributetype)
        self.assertEquals(self.third_attributetype.next_attributetype, self.second_attributetype)

    def test_related_published(self):
        site = Site.objects.get_current()
        self.assertFalse(self.attributetype.related_published)
        params = {'title': 'My second attributetype',
                  'content': 'My second content',
                  'slug': 'my-second-attributetype',
                  'status': PUBLISHED}
        self.second_attributetype = Attributetype.objects.create(**params)
        self.second_attributetype.related.add(self.attributetype)
        self.assertEquals(len(self.attributetype.related_published), 0)

        self.second_attributetype.sites.add(site)
        self.assertEquals(len(self.attributetype.related_published), 1)
        self.assertEquals(len(self.second_attributetype.related_published), 0)

        self.attributetype.status = PUBLISHED
        self.attributetype.save()
        self.attributetype.sites.add(site)
        self.assertEquals(len(self.attributetype.related_published), 1)
        self.assertEquals(len(self.second_attributetype.related_published), 1)


class AttributetypeHtmlContentTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My attributetype',
                  'content': 'My content',
                  'slug': 'my-attributetype'}
        self.attributetype = Attributetype(**params)
        self.original_debug = settings.DEBUG
        self.original_rendering = models_settings.MARKUP_LANGUAGE
        settings.DEBUG = False

    def tearDown(self):
        settings.DEBUG = self.original_debug
        models_settings.MARKUP_LANGUAGE = self.original_rendering

    def test_html_content_default(self):
        models_settings.MARKUP_LANGUAGE = None
        self.assertEquals(self.attributetype.html_content, '<p>My content</p>')

        self.attributetype.content = 'Hello world !\n' \
                             ' this is my content'
        self.assertEquals(self.attributetype.html_content,
                          '<p>Hello world !<br /> this is my content</p>')

    def test_html_content_textitle(self):
        models_settings.MARKUP_LANGUAGE = 'textile'
        self.attributetype.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.attributetype.html_content
        try:
            self.assertEquals(html_content,
                              '\t<p>Hello world !</p>\n\n\t' \
                              '<p>this is my content :</p>\n\n\t' \
                              '<ul>\n\t\t<li>Item 1</li>\n\t\t' \
                              '<li>Item 2</li>\n\t</ul>')
        except AssertionError:
            self.assertEquals(html_content, self.attributetype.content)

    def test_html_content_markdown(self):
        models_settings.MARKUP_LANGUAGE = 'markdown'
        self.attributetype.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.attributetype.html_content
        try:
            self.assertEquals(html_content,
                              '<p>Hello world !</p>\n' \
                              '<p>this is my content :</p>'\
                              '\n<ul>\n<li>Item 1</li>\n' \
                              '<li>Item 2</li>\n</ul>')
        except AssertionError:
            self.assertEquals(html_content, self.attributetype.content)

    def test_html_content_restructuredtext(self):
        models_settings.MARKUP_LANGUAGE = 'restructuredtext'
        self.attributetype.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.attributetype.html_content
        try:
            self.assertEquals(html_content,
                              '<p>Hello world !</p>\n' \
                              '<p>this is my content :</p>'\
                              '\n<ul class="simple">\n<li>Item 1</li>\n' \
                              '<li>Item 2</li>\n</ul>\n')
        except AssertionError:
            self.assertEquals(html_content, self.attributetype.content)

# this class can be removed since the base abstract class is no longer present.
class AttributetypeGetBaseModelTestCase(TestCase):

    def setUp(self):
        self.original_attributetype_base_model = models_settings.ATTRIBUTETYPE_BASE_MODEL

    def tearDown(self):
        models_settings.ATTRIBUTETYPE_BASE_MODEL = self.original_attributetype_base_model

    def test_get_base_model(self):
        models_settings.ATTRIBUTETYPE_BASE_MODEL = ''
        self.assertEquals(get_base_model(), Attributetype)

        models_settings.ATTRIBUTETYPE_BASE_MODEL = 'mymodule.myclass'
        try:
            with warnings.catch_warnings(record=True) as w:
                self.assertEquals(get_base_model(), Attributetype)
                self.assertTrue(issubclass(w[-1].attribute, RuntimeWarning))
        except AttributeError:
            # Fail under Python2.5, because of'warnings.catch_warnings'
            pass

        models_settings.ATTRIBUTETYPE_BASE_MODEL = 'attributeapp.models.Attributetype'
        self.assertEquals(get_base_model(), Attributetype)
