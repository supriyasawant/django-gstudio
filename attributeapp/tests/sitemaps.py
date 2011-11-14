"""Test cases for Attributeapp's sitemaps"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from tagging.models import Tag

from attributeapp.models import Attributetype
from attributeapp.models import Author
from attributeapp.models import Attribute
from attributeapp.managers import PUBLISHED
from attributeapp.sitemaps import AttributetypeSitemap
from attributeapp.sitemaps import AttributeSitemap
from attributeapp.sitemaps import AuthorSitemap
from attributeapp.sitemaps import TagSitemap


class AttributeappSitemapsTestCase(TestCase):
    """Test cases for Sitemaps classes provided"""
    urls = 'attributeapp.tests.urls'

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.attribute = Attribute.objects.create(title='Tests', slug='tests')
        params = {'title': 'My attributetype 1', 'content': 'My content 1',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-1',
                  'status': PUBLISHED}
        self.attributetype_1 = Attributetype.objects.create(**params)
        self.attributetype_1.authors.add(self.author)
        self.attributetype_1.attributes.add(self.attribute)
        self.attributetype_1.sites.add(self.site)

        params = {'title': 'My attributetype 2', 'content': 'My content 2',
                  'tags': 'attributeapp', 'slug': 'my-attributetype-2',
                  'status': PUBLISHED}
        self.attributetype_2 = Attributetype.objects.create(**params)
        self.attributetype_2.authors.add(self.author)
        self.attributetype_2.attributes.add(self.attribute)
        self.attributetype_2.sites.add(self.site)

    def test_attributetype_sitemap(self):
        sitemap = AttributetypeSitemap()
        self.assertEquals(len(sitemap.items()), 2)
        self.assertEquals(sitemap.lastmod(self.attributetype_1),
                          self.attributetype_1.last_update)

    def test_attribute_sitemap(self):
        sitemap = AttributeSitemap()
        self.assertEquals(len(sitemap.items()), 1)
        self.assertEquals(sitemap.lastmod(self.attribute),
                          self.attributetype_2.creation_date)
        self.assertEquals(sitemap.lastmod(Attribute.objects.create(
            title='New', slug='new')), None)
        self.assertEquals(sitemap.priority(self.attribute), '1.0')

    def test_author_sitemap(self):
        sitemap = AuthorSitemap()
        authors = sitemap.items()
        self.assertEquals(len(authors), 1)
        self.assertEquals(sitemap.lastmod(authors[0]),
                          self.attributetype_2.creation_date)
        self.assertEquals(sitemap.lastmod(Author.objects.create(
            username='New', email='new@example.com')), None)
        self.assertEquals(sitemap.location(self.author), '/authors/admin/')

    def test_tag_sitemap(self):
        sitemap = TagSitemap()
        attributeapp_tag = Tag.objects.get(name='attributeapp')
        self.assertEquals(len(sitemap.items()), 2)
        self.assertEquals(sitemap.lastmod(attributeapp_tag),
                          self.attributetype_2.creation_date)
        self.assertEquals(sitemap.priority(attributeapp_tag), '1.0')
        self.assertEquals(sitemap.location(attributeapp_tag), '/tags/attributeapp/')

    def test_attribute_sitemap_zero_division_error(self):
        Attributetype.objects.all().delete()
        attribute_sitemap = AttributeSitemap()
        attribute_sitemap.items()
        self.assertEquals(attribute_sitemap.priority(self.attribute), '0.5')
