"""Test cases for Attributeapp's managers"""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from tagging.models import Tag

from attributeapp.models import Attributetype
from attributeapp.models import Author
from attributeapp.models import Attribute
from attributeapp.managers import PUBLISHED
from attributeapp.managers import tags_published
from attributeapp.managers import attributetypes_published


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
        self.attributes = [
            Attribute.objects.create(title='Attribute 1',
                                    slug='attribute-1'),
            Attribute.objects.create(title='Attribute 2',
                                    slug='attribute-2')]

        params = {'title': 'My attributetype 1', 'content': 'My content 1',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-1',
                  'status': PUBLISHED}
        self.attributetype_1 = Attributetype.objects.create(**params)
        self.attributetype_1.authors.add(self.authors[0])
        self.attributetype_1.attributes.add(*self.attributes)
        self.attributetype_1.sites.add(*self.sites)

        params = {'title': 'My attributetype 2', 'content': 'My content 2',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-2'}
        self.attributetype_2 = Attributetype.objects.create(**params)
        self.attributetype_2.authors.add(*self.authors)
        self.attributetype_2.attributes.add(self.attributes[0])
        self.attributetype_2.sites.add(self.sites[0])

    def test_tags_published(self):
        self.assertEquals(tags_published().count(), Tag.objects.count())
        Tag.objects.create(name='out')
        self.assertNotEquals(tags_published().count(), Tag.objects.count())

    def test_author_published_manager_get_query_set(self):
        self.assertEquals(Author.published.count(), 1)
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        self.assertEquals(Author.published.count(), 2)
        self.attributetype_2.sites.remove(self.sites[0])
        self.attributetype_2.sites.add(self.sites[1])
        self.assertEquals(Author.published.count(), 1)

    def test_attributetypes_published(self):
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 1)
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 2)
        self.attributetype_1.sites.clear()
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 1)
        self.attributetype_1.sites.add(*self.sites)
        self.attributetype_1.start_publication = datetime(2020, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 1)
        self.attributetype_1.start_publication = datetime(2000, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 2)
        self.attributetype_1.end_publication = datetime(2000, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 1)
        self.attributetype_1.end_publication = datetime(2020, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(attributetypes_published(Attributetype.objects.all()).count(), 2)

    def test_attributetype_published_manager_get_query_set(self):
        self.assertEquals(Attributetype.published.count(), 1)
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        self.assertEquals(Attributetype.published.count(), 2)
        self.attributetype_1.sites.clear()
        self.assertEquals(Attributetype.published.count(), 1)
        self.attributetype_1.sites.add(*self.sites)
        self.attributetype_1.start_publication = datetime(2020, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(Attributetype.published.count(), 1)
        self.attributetype_1.start_publication = datetime(2000, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(Attributetype.published.count(), 2)
        self.attributetype_1.end_publication = datetime(2000, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(Attributetype.published.count(), 1)
        self.attributetype_1.end_publication = datetime(2020, 1, 1)
        self.attributetype_1.save()
        self.assertEquals(Attributetype.published.count(), 2)

    def test_attributetype_published_manager_on_site(self):
        self.assertEquals(Attributetype.published.on_site().count(), 2)
        self.attributetype_2.sites.clear()
        self.attributetype_2.sites.add(self.sites[1])
        self.assertEquals(Attributetype.published.on_site().count(), 1)
        self.attributetype_1.sites.clear()
        self.assertEquals(Attributetype.published.on_site().count(), 0)

    def test_attributetype_published_manager_basic_search(self):
        self.assertEquals(Attributetype.published.basic_search('My ').count(), 1)
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        self.assertEquals(Attributetype.published.basic_search('My ').count(), 2)
        self.assertEquals(Attributetype.published.basic_search('1').count(), 1)
        self.assertEquals(Attributetype.published.basic_search('content 1').count(), 2)

    def test_attributetype_published_manager_advanced_search(self):
        attribute = Attribute.objects.create(
            title='SimpleAttribute', slug='simple')
        self.attributetype_2.attributes.add(attribute)
        self.attributetype_2.tags = self.attributetype_2.tags + ', custom'
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        self.assertEquals(
            Attributetype.published.advanced_search('content').count(), 2)
        search = Attributetype.published.advanced_search('content 1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.attributetype_1)
        self.assertEquals(
            Attributetype.published.advanced_search('content 1 or 2').count(), 2)
        self.assertEquals(
            Attributetype.published.advanced_search('content 1 and 2').count(), 0)
        self.assertEquals(
            Attributetype.published.advanced_search('content 1 2').count(), 0)
        self.assertEquals(
            Attributetype.published.advanced_search('"My content" 1 or 2').count(), 2)
        self.assertEquals(
            Attributetype.published.advanced_search('-"My content" 2').count(), 0)
        search = Attributetype.published.advanced_search('content -1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.attributetype_2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content attribute:SimpleAttribute').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'content attribute:simple').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'content attribute:"Attribute 1"').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content attribute:"attribute-1"').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content attribute:"attribute-2"').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'content tag:attributeapp').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content tag:custom').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'content author:webmaster').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content author:contributor').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'content author:webmaster tag:attributeapp').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content author:webmaster tag:custom').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:webmaster content) my').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:webmaster) or (author:contributor)').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:webmaster) (author:contributor)').count(), 0)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:webmaster content) 1').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:webmaster content) or 2').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:contributor content) or 1').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:contributor content) or 2').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:webmaster or ("hello world")) and 2').count(), 1)

        # Complex queries
        self.assertEquals(Attributetype.published.advanced_search(
            '(author:admin and "content 1") or author:webmaster').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:admin and ("content 1" or author:webmaster)').count(), 0)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:admin and "content 1" or author:webmaster').count(), 0)
        self.assertEquals(Attributetype.published.advanced_search(
            '-(author:webmaster and "content 1")').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            '-(-author:webmaster and "content 1")').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'attribute:"attribute -1" or author:"web master"').count(), 0)
        self.assertEquals(Attributetype.published.advanced_search(
            'attribute:"attribute-1" or author:"webmaster"').count(), 2)

        # Wildcards
        self.assertEquals(Attributetype.published.advanced_search(
            'author:webm*').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:*bmas*').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:*master').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:*master attribute:*ory-2').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:*master or attribute:cate*').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'attribute:*ate*').count(), 2)
        self.assertEquals(Attributetype.published.advanced_search(
            'author:"webmast*"').count(), 0)
        self.assertEquals(Attributetype.published.advanced_search(
            'tag:"attributeapp*"').count(), 0)
        self.assertEquals(Attributetype.published.advanced_search(
            'tag:*inni*').count(), 2)

    def test_attributetype_published_manager_advanced_search_with_punctuation(self):
        self.attributetype_2.content = 'How are you today ? Fine thank you ! OK.'
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        self.assertEquals(Attributetype.published.advanced_search(
            'today ?').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            'today or ! or .').count(), 1)
        self.assertEquals(Attributetype.published.advanced_search(
            '"you today ?"').count(), 1)

    def test_attributetype_published_manager_search(self):
        self.attributetype_2.content = self.attributetype_2.content + ' * '
        self.attributetype_2.status = PUBLISHED
        self.attributetype_2.save()
        # Be sure that basic_search does not return
        # the same results of advanced_search
        self.assertNotEquals(
            Attributetype.published.basic_search('content 1').count(),
            Attributetype.published.advanced_search('content 1').count())
        # Now check the fallback with the '*' pattern
        # which will fails advanced search
        self.assertEquals(Attributetype.published.search('*').count(), 1)
