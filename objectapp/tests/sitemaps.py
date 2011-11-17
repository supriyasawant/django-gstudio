"""Test cases for Objectapp's sitemaps"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from tagging.models import Tag

from objectapp.models import Gbobject
from objectapp.models import Author
from objectapp.models import Objecttype
from objectapp.managers import PUBLISHED
from objectapp.sitemaps import GbobjectSitemap
from objectapp.sitemaps import ObjecttypeSitemap
from objectapp.sitemaps import AuthorSitemap
from objectapp.sitemaps import TagSitemap


class ObjectappSitemapsTestCase(TestCase):
    """Test cases for Sitemaps classes provided"""
    urls = 'objectapp.tests.urls'

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.Objecttype = Objecttype.objects.create(title='Tests', slug='tests')
        params = {'title': 'My gbobject 1', 'content': 'My content 1',
                  'tags': 'objectapp, test', 'slug': 'my-gbobject-1',
                  'status': PUBLISHED}
        self.gbobject_1 = Gbobject.objects.create(**params)
        self.gbobject_1.authors.add(self.author)
        self.gbobject_1.objecttypes.add(self.Objecttype)
        self.gbobject_1.sites.add(self.site)

        params = {'title': 'My gbobject 2', 'content': 'My content 2',
                  'tags': 'objectapp', 'slug': 'my-gbobject-2',
                  'status': PUBLISHED}
        self.gbobject_2 = Gbobject.objects.create(**params)
        self.gbobject_2.authors.add(self.author)
        self.gbobject_2.objecttypes.add(self.Objecttype)
        self.gbobject_2.sites.add(self.site)

    def test_gbobject_sitemap(self):
        sitemap = GbobjectSitemap()
        self.assertEquals(len(sitemap.items()), 2)
        self.assertEquals(sitemap.lastmod(self.gbobject_1),
                          self.gbobject_1.last_update)

    def test_Objecttype_sitemap(self):
        sitemap = ObjecttypeSitemap()
        self.assertEquals(len(sitemap.items()), 1)
        self.assertEquals(sitemap.lastmod(self.Objecttype),
                          self.gbobject_2.creation_date)
        self.assertEquals(sitemap.lastmod(Objecttype.objects.create(
            title='New', slug='new')), None)
        self.assertEquals(sitemap.priority(self.Objecttype), '1.0')

    def test_author_sitemap(self):
        sitemap = AuthorSitemap()
        authors = sitemap.items()
        self.assertEquals(len(authors), 1)
        self.assertEquals(sitemap.lastmod(authors[0]),
                          self.gbobject_2.creation_date)
        self.assertEquals(sitemap.lastmod(Author.objects.create(
            username='New', email='new@example.com')), None)
        self.assertEquals(sitemap.location(self.author), '/authors/admin/')

    def test_tag_sitemap(self):
        sitemap = TagSitemap()
        objectapp_tag = Tag.objects.get(name='objectapp')
        self.assertEquals(len(sitemap.items()), 2)
        self.assertEquals(sitemap.lastmod(objectapp_tag),
                          self.gbobject_2.creation_date)
        self.assertEquals(sitemap.priority(objectapp_tag), '1.0')
        self.assertEquals(sitemap.location(objectapp_tag), '/tags/objectapp/')

    def test_Objecttype_sitemap_zero_division_error(self):
        Gbobject.objects.all().delete()
        Objecttype_sitemap = ObjecttypeSitemap()
        Objecttype_sitemap.items()
        self.assertEquals(Objecttype_sitemap.priority(self.Objecttype), '0.5')
