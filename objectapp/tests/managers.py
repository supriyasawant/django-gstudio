"""Test cases for Objectapp's managers"""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from tagging.models import Tag

from objectapp.models import GBObject
from objectapp.models import Author
from objectapp.models import Objecttype
from objectapp.managers import PUBLISHED
from objectapp.managers import tags_published
from objectapp.managers import gbobjects_published


class ManagersTestCase(TestCase):

    def setUp(self):
        self.sites = [
            Site.objects.get_current(),
            Site.objects.create(domain='http://domain.com',
                                name='Domain.com')]
        self.authors = [
            User.objects.create_user(username='webmaster',
                                     email='webmaster@example.com'),
            User.objects.create_user(username='contributor',
                                     email='contributor@example.com')]
        self.objecttypes = [
            Objecttype.objects.create(title='Objecttype 1',
                                    slug='objecttype-1'),
            Objecttype.objects.create(title='Objecttype 2',
                                    slug='objecttype-2')]

        params = {'title': 'My gbobject 1', 'content': 'My content 1',
                  'tags': 'objectapp, test', 'slug': 'my-gbobject-1',
                  'status': PUBLISHED}
        self.gbobject_1 = GBObject.objects.create(**params)
        self.gbobject_1.authors.add(self.authors[0])
        self.gbobject_1.objecttypes.add(*self.objecttypes)
        self.gbobject_1.sites.add(*self.sites)

        params = {'title': 'My gbobject 2', 'content': 'My content 2',
                  'tags': 'objectapp, test', 'slug': 'my-gbobject-2'}
        self.gbobject_2 = GBObject.objects.create(**params)
        self.gbobject_2.authors.add(*self.authors)
        self.gbobject_2.objecttypes.add(self.objecttypes[0])
        self.gbobject_2.sites.add(self.sites[0])

    def test_tags_published(self):
        self.assertEquals(tags_published().count(), Tag.objects.count())
        Tag.objects.create(name='out')
        self.assertNotEquals(tags_published().count(), Tag.objects.count())

    def test_author_published_manager_get_query_set(self):
        self.assertEquals(Author.published.count(), 1)
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        self.assertEquals(Author.published.count(), 2)
        self.gbobject_2.sites.remove(self.sites[0])
        self.gbobject_2.sites.add(self.sites[1])
        self.assertEquals(Author.published.count(), 1)

    def test_gbobjects_published(self):
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 1)
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 2)
        self.gbobject_1.sites.clear()
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 1)
        self.gbobject_1.sites.add(*self.sites)
        self.gbobject_1.start_publication = datetime(2020, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 1)
        self.gbobject_1.start_publication = datetime(2000, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 2)
        self.gbobject_1.end_publication = datetime(2000, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 1)
        self.gbobject_1.end_publication = datetime(2020, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(gbobjects_published(GBObject.objects.all()).count(), 2)

    def test_gbobject_published_manager_get_query_set(self):
        self.assertEquals(GBObject.published.count(), 1)
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        self.assertEquals(GBObject.published.count(), 2)
        self.gbobject_1.sites.clear()
        self.assertEquals(GBObject.published.count(), 1)
        self.gbobject_1.sites.add(*self.sites)
        self.gbobject_1.start_publication = datetime(2020, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(GBObject.published.count(), 1)
        self.gbobject_1.start_publication = datetime(2000, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(GBObject.published.count(), 2)
        self.gbobject_1.end_publication = datetime(2000, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(GBObject.published.count(), 1)
        self.gbobject_1.end_publication = datetime(2020, 1, 1)
        self.gbobject_1.save()
        self.assertEquals(GBObject.published.count(), 2)

    def test_gbobject_published_manager_on_site(self):
        self.assertEquals(GBObject.published.on_site().count(), 2)
        self.gbobject_2.sites.clear()
        self.gbobject_2.sites.add(self.sites[1])
        self.assertEquals(GBObject.published.on_site().count(), 1)
        self.gbobject_1.sites.clear()
        self.assertEquals(GBObject.published.on_site().count(), 0)

    def test_gbobject_published_manager_basic_search(self):
        self.assertEquals(GBObject.published.basic_search('My ').count(), 1)
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        self.assertEquals(GBObject.published.basic_search('My ').count(), 2)
        self.assertEquals(GBObject.published.basic_search('1').count(), 1)
        self.assertEquals(GBObject.published.basic_search('content 1').count(), 2)

    def test_gbobject_published_manager_advanced_search(self):
        objecttype = Objecttype.objects.create(
            title='SimpleObjecttype', slug='simple')
        self.gbobject_2.objecttypes.add(objecttype)
        self.gbobject_2.tags = self.gbobject_2.tags + ', custom'
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        self.assertEquals(
            GBObject.published.advanced_search('content').count(), 2)
        search = GBObject.published.advanced_search('content 1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.gbobject_1)
        self.assertEquals(
            GBObject.published.advanced_search('content 1 or 2').count(), 2)
        self.assertEquals(
            GBObject.published.advanced_search('content 1 and 2').count(), 0)
        self.assertEquals(
            GBObject.published.advanced_search('content 1 2').count(), 0)
        self.assertEquals(
            GBObject.published.advanced_search('"My content" 1 or 2').count(), 2)
        self.assertEquals(
            GBObject.published.advanced_search('-"My content" 2').count(), 0)
        search = GBObject.published.advanced_search('content -1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.gbobject_2)
        self.assertEquals(GBObject.published.advanced_search(
            'content objecttype:SimpleObjecttype').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'content objecttype:simple').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'content objecttype:"Objecttype 1"').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'content objecttype:"objecttype-1"').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'content objecttype:"objecttype-2"').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'content tag:objectapp').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'content tag:custom').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'content author:webmaster').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'content author:contributor').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'content author:webmaster tag:objectapp').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'content author:webmaster tag:custom').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:webmaster content) my').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:webmaster) or (author:contributor)').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:webmaster) (author:contributor)').count(), 0)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:webmaster content) 1').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:webmaster content) or 2').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:contributor content) or 1').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:contributor content) or 2').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            '(author:webmaster or ("hello world")) and 2').count(), 1)

        # Complex queries
        self.assertEquals(GBObject.published.advanced_search(
            '(author:admin and "content 1") or author:webmaster').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'author:admin and ("content 1" or author:webmaster)').count(), 0)
        self.assertEquals(GBObject.published.advanced_search(
            'author:admin and "content 1" or author:webmaster').count(), 0)
        self.assertEquals(GBObject.published.advanced_search(
            '-(author:webmaster and "content 1")').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            '-(-author:webmaster and "content 1")').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'objecttype:"objecttype -1" or author:"web master"').count(), 0)
        self.assertEquals(GBObject.published.advanced_search(
            'objecttype:"objecttype-1" or author:"webmaster"').count(), 2)

        # Wildcards
        self.assertEquals(GBObject.published.advanced_search(
            'author:webm*').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'author:*bmas*').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'author:*master').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'author:*master objecttype:*ory-2').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'author:*master or objecttype:cate*').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'objecttype:*ate*').count(), 2)
        self.assertEquals(GBObject.published.advanced_search(
            'author:"webmast*"').count(), 0)
        self.assertEquals(GBObject.published.advanced_search(
            'tag:"objectapp*"').count(), 0)
        self.assertEquals(GBObject.published.advanced_search(
            'tag:*inni*').count(), 2)

    def test_gbobject_published_manager_advanced_search_with_punctuation(self):
        self.gbobject_2.content = 'How are you today ? Fine thank you ! OK.'
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        self.assertEquals(GBObject.published.advanced_search(
            'today ?').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            'today or ! or .').count(), 1)
        self.assertEquals(GBObject.published.advanced_search(
            '"you today ?"').count(), 1)

    def test_gbobject_published_manager_search(self):
        self.gbobject_2.content = self.gbobject_2.content + ' * '
        self.gbobject_2.status = PUBLISHED
        self.gbobject_2.save()
        # Be sure that basic_search does not return
        # the same results of advanced_search
        self.assertNotEquals(
            GBObject.published.basic_search('content 1').count(),
            GBObject.published.advanced_search('content 1').count())
        # Now check the fallback with the '*' pattern
        # which will fails advanced search
        self.assertEquals(GBObject.published.search('*').count(), 1)
