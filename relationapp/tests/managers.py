"""Test cases for Relationapp's managers"""
from datetime import datetime

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from tagging.models import Tag

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.models import Relation
from relationapp.managers import PUBLISHED
from relationapp.managers import tags_published
from relationapp.managers import relationtypes_published


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
        self.relations = [
            Relation.objects.create(title='Relation 1',
                                    slug='relation-1'),
            Relation.objects.create(title='Relation 2',
                                    slug='relation-2')]

        params = {'title': 'My relationtype 1', 'content': 'My content 1',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-1',
                  'status': PUBLISHED}
        self.relationtype_1 = Relationtype.objects.create(**params)
        self.relationtype_1.authors.add(self.authors[0])
        self.relationtype_1.relations.add(*self.relations)
        self.relationtype_1.sites.add(*self.sites)

        params = {'title': 'My relationtype 2', 'content': 'My content 2',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-2'}
        self.relationtype_2 = Relationtype.objects.create(**params)
        self.relationtype_2.authors.add(*self.authors)
        self.relationtype_2.relations.add(self.relations[0])
        self.relationtype_2.sites.add(self.sites[0])

    def test_tags_published(self):
        self.assertEquals(tags_published().count(), Tag.objects.count())
        Tag.objects.create(name='out')
        self.assertNotEquals(tags_published().count(), Tag.objects.count())

    def test_author_published_manager_get_query_set(self):
        self.assertEquals(Author.published.count(), 1)
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        self.assertEquals(Author.published.count(), 2)
        self.relationtype_2.sites.remove(self.sites[0])
        self.relationtype_2.sites.add(self.sites[1])
        self.assertEquals(Author.published.count(), 1)

    def test_relationtypes_published(self):
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 1)
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 2)
        self.relationtype_1.sites.clear()
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 1)
        self.relationtype_1.sites.add(*self.sites)
        self.relationtype_1.start_publication = datetime(2020, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 1)
        self.relationtype_1.start_publication = datetime(2000, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 2)
        self.relationtype_1.end_publication = datetime(2000, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 1)
        self.relationtype_1.end_publication = datetime(2020, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(relationtypes_published(Relationtype.objects.all()).count(), 2)

    def test_relationtype_published_manager_get_query_set(self):
        self.assertEquals(Relationtype.published.count(), 1)
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        self.assertEquals(Relationtype.published.count(), 2)
        self.relationtype_1.sites.clear()
        self.assertEquals(Relationtype.published.count(), 1)
        self.relationtype_1.sites.add(*self.sites)
        self.relationtype_1.start_publication = datetime(2020, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(Relationtype.published.count(), 1)
        self.relationtype_1.start_publication = datetime(2000, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(Relationtype.published.count(), 2)
        self.relationtype_1.end_publication = datetime(2000, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(Relationtype.published.count(), 1)
        self.relationtype_1.end_publication = datetime(2020, 1, 1)
        self.relationtype_1.save()
        self.assertEquals(Relationtype.published.count(), 2)

    def test_relationtype_published_manager_on_site(self):
        self.assertEquals(Relationtype.published.on_site().count(), 2)
        self.relationtype_2.sites.clear()
        self.relationtype_2.sites.add(self.sites[1])
        self.assertEquals(Relationtype.published.on_site().count(), 1)
        self.relationtype_1.sites.clear()
        self.assertEquals(Relationtype.published.on_site().count(), 0)

    def test_relationtype_published_manager_basic_search(self):
        self.assertEquals(Relationtype.published.basic_search('My ').count(), 1)
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        self.assertEquals(Relationtype.published.basic_search('My ').count(), 2)
        self.assertEquals(Relationtype.published.basic_search('1').count(), 1)
        self.assertEquals(Relationtype.published.basic_search('content 1').count(), 2)

    def test_relationtype_published_manager_advanced_search(self):
        relation = Relation.objects.create(
            title='SimpleRelation', slug='simple')
        self.relationtype_2.relations.add(relation)
        self.relationtype_2.tags = self.relationtype_2.tags + ', custom'
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        self.assertEquals(
            Relationtype.published.advanced_search('content').count(), 2)
        search = Relationtype.published.advanced_search('content 1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.relationtype_1)
        self.assertEquals(
            Relationtype.published.advanced_search('content 1 or 2').count(), 2)
        self.assertEquals(
            Relationtype.published.advanced_search('content 1 and 2').count(), 0)
        self.assertEquals(
            Relationtype.published.advanced_search('content 1 2').count(), 0)
        self.assertEquals(
            Relationtype.published.advanced_search('"My content" 1 or 2').count(), 2)
        self.assertEquals(
            Relationtype.published.advanced_search('-"My content" 2').count(), 0)
        search = Relationtype.published.advanced_search('content -1')
        self.assertEquals(search.count(), 1)
        self.assertEquals(search.all()[0], self.relationtype_2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content relation:SimpleRelation').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'content relation:simple').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'content relation:"Relation 1"').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content relation:"relation-1"').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content relation:"relation-2"').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'content tag:relationapp').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content tag:custom').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'content author:webmaster').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content author:contributor').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'content author:webmaster tag:relationapp').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content author:webmaster tag:custom').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'content 1 or 2 author:webmaster').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:webmaster content) my').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:webmaster) or (author:contributor)').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:webmaster) (author:contributor)').count(), 0)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:webmaster content) 1').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:webmaster content) or 2').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:contributor content) or 1').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:contributor content) or 2').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:webmaster or ("hello world")) and 2').count(), 1)

        # Complex queries
        self.assertEquals(Relationtype.published.advanced_search(
            '(author:admin and "content 1") or author:webmaster').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:admin and ("content 1" or author:webmaster)').count(), 0)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:admin and "content 1" or author:webmaster').count(), 0)
        self.assertEquals(Relationtype.published.advanced_search(
            '-(author:webmaster and "content 1")').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            '-(-author:webmaster and "content 1")').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'relation:"relation -1" or author:"web master"').count(), 0)
        self.assertEquals(Relationtype.published.advanced_search(
            'relation:"relation-1" or author:"webmaster"').count(), 2)

        # Wildcards
        self.assertEquals(Relationtype.published.advanced_search(
            'author:webm*').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:*bmas*').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:*master').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:*master relation:*ory-2').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:*master or relation:cate*').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'relation:*ate*').count(), 2)
        self.assertEquals(Relationtype.published.advanced_search(
            'author:"webmast*"').count(), 0)
        self.assertEquals(Relationtype.published.advanced_search(
            'tag:"relationapp*"').count(), 0)
        self.assertEquals(Relationtype.published.advanced_search(
            'tag:*inni*').count(), 2)

    def test_relationtype_published_manager_advanced_search_with_punctuation(self):
        self.relationtype_2.content = 'How are you today ? Fine thank you ! OK.'
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        self.assertEquals(Relationtype.published.advanced_search(
            'today ?').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            'today or ! or .').count(), 1)
        self.assertEquals(Relationtype.published.advanced_search(
            '"you today ?"').count(), 1)

    def test_relationtype_published_manager_search(self):
        self.relationtype_2.content = self.relationtype_2.content + ' * '
        self.relationtype_2.status = PUBLISHED
        self.relationtype_2.save()
        # Be sure that basic_search does not return
        # the same results of advanced_search
        self.assertNotEquals(
            Relationtype.published.basic_search('content 1').count(),
            Relationtype.published.advanced_search('content 1').count())
        # Now check the fallback with the '*' pattern
        # which will fails advanced search
        self.assertEquals(Relationtype.published.search('*').count(), 1)
