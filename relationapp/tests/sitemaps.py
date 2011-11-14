"""Test cases for Relationapp's sitemaps"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from tagging.models import Tag

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.models import Relation
from relationapp.managers import PUBLISHED
from relationapp.sitemaps import RelationtypeSitemap
from relationapp.sitemaps import RelationSitemap
from relationapp.sitemaps import AuthorSitemap
from relationapp.sitemaps import TagSitemap


class RelationappSitemapsTestCase(TestCase):
    """Test cases for Sitemaps classes provided"""
    urls = 'relationapp.tests.urls'

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.relation = Relation.objects.create(title='Tests', slug='tests')
        params = {'title': 'My relationtype 1', 'content': 'My content 1',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-1',
                  'status': PUBLISHED}
        self.relationtype_1 = Relationtype.objects.create(**params)
        self.relationtype_1.authors.add(self.author)
        self.relationtype_1.relations.add(self.relation)
        self.relationtype_1.sites.add(self.site)

        params = {'title': 'My relationtype 2', 'content': 'My content 2',
                  'tags': 'relationapp', 'slug': 'my-relationtype-2',
                  'status': PUBLISHED}
        self.relationtype_2 = Relationtype.objects.create(**params)
        self.relationtype_2.authors.add(self.author)
        self.relationtype_2.relations.add(self.relation)
        self.relationtype_2.sites.add(self.site)

    def test_relationtype_sitemap(self):
        sitemap = RelationtypeSitemap()
        self.assertEquals(len(sitemap.items()), 2)
        self.assertEquals(sitemap.lastmod(self.relationtype_1),
                          self.relationtype_1.last_update)

    def test_relation_sitemap(self):
        sitemap = RelationSitemap()
        self.assertEquals(len(sitemap.items()), 1)
        self.assertEquals(sitemap.lastmod(self.relation),
                          self.relationtype_2.creation_date)
        self.assertEquals(sitemap.lastmod(Relation.objects.create(
            title='New', slug='new')), None)
        self.assertEquals(sitemap.priority(self.relation), '1.0')

    def test_author_sitemap(self):
        sitemap = AuthorSitemap()
        authors = sitemap.items()
        self.assertEquals(len(authors), 1)
        self.assertEquals(sitemap.lastmod(authors[0]),
                          self.relationtype_2.creation_date)
        self.assertEquals(sitemap.lastmod(Author.objects.create(
            username='New', email='new@example.com')), None)
        self.assertEquals(sitemap.location(self.author), '/authors/admin/')

    def test_tag_sitemap(self):
        sitemap = TagSitemap()
        relationapp_tag = Tag.objects.get(name='relationapp')
        self.assertEquals(len(sitemap.items()), 2)
        self.assertEquals(sitemap.lastmod(relationapp_tag),
                          self.relationtype_2.creation_date)
        self.assertEquals(sitemap.priority(relationapp_tag), '1.0')
        self.assertEquals(sitemap.location(relationapp_tag), '/tags/relationapp/')

    def test_relation_sitemap_zero_division_error(self):
        Relationtype.objects.all().delete()
        relation_sitemap = RelationSitemap()
        relation_sitemap.items()
        self.assertEquals(relation_sitemap.priority(self.relation), '0.5')
