"""Test cases for Gstudio's Objecttype"""
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

from gstudio import models
from gstudio.models import Objecttype
from gstudio.managers import PUBLISHED
from gstudio.models import get_base_model
from gstudio.models import Objecttype
from gstudio import models as models_settings
from gstudio import url_shortener as shortener_settings


class ObjecttypeTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My objecttype',
                  'content': 'My content',
                  'slug': 'my-objecttype'}
        self.objecttype = Objecttype.objects.create(**params)

    def test_discussions(self):
        site = Site.objects.get_current()
        self.assertEquals(self.objecttype.discussions.count(), 0)
        self.assertEquals(self.objecttype.comments.count(), 0)
        self.assertEquals(self.objecttype.pingbacks.count(), 0)
        self.assertEquals(self.objecttype.trackbacks.count(), 0)

        comments.get_model().objects.create(comment='My Comment 1',
                                            content_object=self.objecttype,
                                            site=site)
        self.assertEquals(self.objecttype.discussions.count(), 1)
        self.assertEquals(self.objecttype.comments.count(), 1)
        self.assertEquals(self.objecttype.pingbacks.count(), 0)
        self.assertEquals(self.objecttype.trackbacks.count(), 0)

        comments.get_model().objects.create(comment='My Comment 2',
                                            content_object=self.objecttype,
                                            site=site, is_public=False)
        self.assertEquals(self.objecttype.discussions.count(), 1)
        self.assertEquals(self.objecttype.comments.count(), 1)
        self.assertEquals(self.objecttype.pingbacks.count(), 0)
        self.assertEquals(self.objecttype.trackbacks.count(), 0)

        author = User.objects.create_user(username='webmaster',
                                          email='webmaster@example.com')

        comment = comments.get_model().objects.create(
            comment='My Comment 3',
            content_object=self.objecttype,
            site=Site.objects.create(domain='http://toto.com',
                                     name='Toto.com'))
        comment.flags.create(user=author, flag=CommentFlag.MODERATOR_APPROVAL)
        self.assertEquals(self.objecttype.discussions.count(), 2)
        self.assertEquals(self.objecttype.comments.count(), 2)
        self.assertEquals(self.objecttype.pingbacks.count(), 0)
        self.assertEquals(self.objecttype.trackbacks.count(), 0)

        comment = comments.get_model().objects.create(
            comment='My Pingback 1', content_object=self.objecttype, site=site)
        comment.flags.create(user=author, flag='pingback')
        self.assertEquals(self.objecttype.discussions.count(), 3)
        self.assertEquals(self.objecttype.comments.count(), 2)
        self.assertEquals(self.objecttype.pingbacks.count(), 1)
        self.assertEquals(self.objecttype.trackbacks.count(), 0)

        comment = comments.get_model().objects.create(
            comment='My Trackback 1', content_object=self.objecttype, site=site)
        comment.flags.create(user=author, flag='trackback')
        self.assertEquals(self.objecttype.discussions.count(), 4)
        self.assertEquals(self.objecttype.comments.count(), 2)
        self.assertEquals(self.objecttype.pingbacks.count(), 1)
        self.assertEquals(self.objecttype.trackbacks.count(), 1)

    def test_str(self):
        self.assertEquals(str(self.objecttype), 'My objecttype: draft')

    def test_word_count(self):
        self.assertEquals(self.objecttype.word_count, 2)

    def test_comments_are_open(self):
        original_auto_close = models.AUTO_CLOSE_COMMENTS_AFTER
        models.AUTO_CLOSE_COMMENTS_AFTER = None
        self.assertEquals(self.objecttype.comments_are_open, True)
        models.AUTO_CLOSE_COMMENTS_AFTER = 5
        self.objecttype.start_publication = datetime.now() - timedelta(days=7)
        self.objecttype.save()
        self.assertEquals(self.objecttype.comments_are_open, False)

        models.AUTO_CLOSE_COMMENTS_AFTER = original_auto_close

    def test_is_actual(self):
        self.assertTrue(self.objecttype.is_actual)
        self.objecttype.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.objecttype.is_actual)
        self.objecttype.start_publication = datetime.now()
        self.assertTrue(self.objecttype.is_actual)
        self.objecttype.end_publication = datetime(2000, 3, 15)
        self.assertFalse(self.objecttype.is_actual)

    def test_is_visible(self):
        self.assertFalse(self.objecttype.is_visible)
        self.objecttype.status = PUBLISHED
        self.assertTrue(self.objecttype.is_visible)
        self.objecttype.start_publication = datetime(2020, 3, 15)
        self.assertFalse(self.objecttype.is_visible)

    def test_short_url(self):
        original_shortener = shortener_settings.URL_SHORTENER_BACKEND
        shortener_settings.URL_SHORTENER_BACKEND = 'gstudio.url_shortener.'\
                                                   'backends.default'
        self.assertEquals(self.objecttype.short_url,
                          'http://example.com' +
                          reverse('gstudio_objecttype_shortlink',
                                  args=[self.objecttype.pk]))
        shortener_settings.URL_SHORTENER_BACKEND = original_shortener

    def test_previous_objecttype(self):
        site = Site.objects.get_current()
        self.assertFalse(self.objecttype.previous_objecttype)
        params = {'title': 'My second objecttype',
                  'content': 'My second content',
                  'slug': 'my-second-objecttype',
                  'creation_date': datetime(2000, 1, 1),
                  'status': PUBLISHED}
        self.second_objecttype = Objecttype.objects.create(**params)
        self.second_objecttype.sites.add(site)
        self.assertEquals(self.objecttype.previous_objecttype, self.second_objecttype)
        params = {'title': 'My third objecttype',
                  'content': 'My third content',
                  'slug': 'my-third-objecttype',
                  'creation_date': datetime(2001, 1, 1),
                  'status': PUBLISHED}
        self.third_objecttype = Objecttype.objects.create(**params)
        self.third_objecttype.sites.add(site)
        self.assertEquals(self.objecttype.previous_objecttype, self.third_objecttype)
        self.assertEquals(self.third_objecttype.previous_objecttype, self.second_objecttype)

    def test_next_objecttype(self):
        site = Site.objects.get_current()
        self.assertFalse(self.objecttype.next_objecttype)
        params = {'title': 'My second objecttype',
                  'content': 'My second content',
                  'slug': 'my-second-objecttype',
                  'creation_date': datetime(2100, 1, 1),
                  'status': PUBLISHED}
        self.second_objecttype = Objecttype.objects.create(**params)
        self.second_objecttype.sites.add(site)
        self.assertEquals(self.objecttype.next_objecttype, self.second_objecttype)
        params = {'title': 'My third objecttype',
                  'content': 'My third content',
                  'slug': 'my-third-objecttype',
                  'creation_date': datetime(2050, 1, 1),
                  'status': PUBLISHED}
        self.third_objecttype = Objecttype.objects.create(**params)
        self.third_objecttype.sites.add(site)
        self.assertEquals(self.objecttype.next_objecttype, self.third_objecttype)
        self.assertEquals(self.third_objecttype.next_objecttype, self.second_objecttype)

    def test_related_published(self):
        site = Site.objects.get_current()
        self.assertFalse(self.objecttype.related_published)
        params = {'title': 'My second objecttype',
                  'content': 'My second content',
                  'slug': 'my-second-objecttype',
                  'status': PUBLISHED}
        self.second_objecttype = Objecttype.objects.create(**params)
        self.second_objecttype.related.add(self.objecttype)
        self.assertEquals(len(self.objecttype.related_published), 0)

        self.second_objecttype.sites.add(site)
        self.assertEquals(len(self.objecttype.related_published), 1)
        self.assertEquals(len(self.second_objecttype.related_published), 0)

        self.objecttype.status = PUBLISHED
        self.objecttype.save()
        self.objecttype.sites.add(site)
        self.assertEquals(len(self.objecttype.related_published), 1)
        self.assertEquals(len(self.second_objecttype.related_published), 1)


class ObjecttypeHtmlContentTestCase(TestCase):

    def setUp(self):
        params = {'title': 'My objecttype',
                  'content': 'My content',
                  'slug': 'my-objecttype'}
        self.objecttype = Objecttype(**params)
        self.original_debug = settings.DEBUG
        self.original_rendering = models_settings.MARKUP_LANGUAGE
        settings.DEBUG = False

    def tearDown(self):
        settings.DEBUG = self.original_debug
        models_settings.MARKUP_LANGUAGE = self.original_rendering

    def test_html_content_default(self):
        models_settings.MARKUP_LANGUAGE = None
        self.assertEquals(self.objecttype.html_content, '<p>My content</p>')

        self.objecttype.content = 'Hello world !\n' \
                             ' this is my content'
        self.assertEquals(self.objecttype.html_content,
                          '<p>Hello world !<br /> this is my content</p>')

    def test_html_content_textitle(self):
        models_settings.MARKUP_LANGUAGE = 'textile'
        self.objecttype.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.objecttype.html_content
        try:
            self.assertEquals(html_content,
                              '\t<p>Hello world !</p>\n\n\t' \
                              '<p>this is my content :</p>\n\n\t' \
                              '<ul>\n\t\t<li>Item 1</li>\n\t\t' \
                              '<li>Item 2</li>\n\t</ul>')
        except AssertionError:
            self.assertEquals(html_content, self.objecttype.content)

    def test_html_content_markdown(self):
        models_settings.MARKUP_LANGUAGE = 'markdown'
        self.objecttype.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.objecttype.html_content
        try:
            self.assertEquals(html_content,
                              '<p>Hello world !</p>\n' \
                              '<p>this is my content :</p>'\
                              '\n<ul>\n<li>Item 1</li>\n' \
                              '<li>Item 2</li>\n</ul>')
        except AssertionError:
            self.assertEquals(html_content, self.objecttype.content)

    def test_html_content_restructuredtext(self):
        models_settings.MARKUP_LANGUAGE = 'restructuredtext'
        self.objecttype.content = 'Hello world !\n\n' \
                             'this is my content :\n\n' \
                             '* Item 1\n* Item 2'
        html_content = self.objecttype.html_content
        try:
            self.assertEquals(html_content,
                              '<p>Hello world !</p>\n' \
                              '<p>this is my content :</p>'\
                              '\n<ul class="simple">\n<li>Item 1</li>\n' \
                              '<li>Item 2</li>\n</ul>\n')
        except AssertionError:
            self.assertEquals(html_content, self.objecttype.content)

# this class can be removed since the base abstract class is no longer present.
class ObjecttypeGetBaseModelTestCase(TestCase):

    def setUp(self):
        self.original_objecttype_base_model = models_settings.OBJECTTYPE_BASE_MODEL

    def tearDown(self):
        models_settings.OBJECTTYPE_BASE_MODEL = self.original_objecttype_base_model

    def test_get_base_model(self):
        models_settings.OBJECTTYPE_BASE_MODEL = ''
        self.assertEquals(get_base_model(), Objecttype)

        models_settings.OBJECTTYPE_BASE_MODEL = 'mymodule.myclass'
        try:
            with warnings.catch_warnings(record=True) as w:
                self.assertEquals(get_base_model(), Objecttype)
                self.assertTrue(issubclass(w[-1].metatype, RuntimeWarning))
        except AttributeError:
            # Fail under Python2.5, because of'warnings.catch_warnings'
            pass

        models_settings.OBJECTTYPE_BASE_MODEL = 'gstudio.models.Objecttype'
        self.assertEquals(get_base_model(), Objecttype)
