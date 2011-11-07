"""Test cases for Gstudio's feeds"""
from datetime import datetime

from django.test import TestCase
from django.conf import settings
from django.contrib import comments
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.utils.feedgenerator import Atom1Feed
from django.utils.feedgenerator import DefaultFeed
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType

from tagging.models import Tag

from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.managers import PUBLISHED
from gstudio import feeds
from gstudio.feeds import ObjecttypeFeed
from gstudio.feeds import LatestObjecttypes
from gstudio.feeds import MetatypeObjecttypes
from gstudio.feeds import AuthorObjecttypes
from gstudio.feeds import TagObjecttypes
from gstudio.feeds import SearchObjecttypes
from gstudio.feeds import ObjecttypeDiscussions
from gstudio.feeds import ObjecttypeComments
from gstudio.feeds import ObjecttypePingbacks
from gstudio.feeds import ObjecttypeTrackbacks


class GstudioFeedsTestCase(TestCase):
    """Test cases for the Feed classes provided"""
    urls = 'gstudio.tests.urls'

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.metatype = Metatype.objects.create(title='Tests', slug='tests')
        self.objecttype_ct_id = ContentType.objects.get_for_model(Objecttype).pk

    def create_published_objecttype(self):
        params = {'title': 'My test objecttype',
                  'content': 'My test content with image '
                  '<img src="/image.jpg" />',
                  'slug': 'my-test-objecttype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        objecttype = Objecttype.objects.create(**params)
        objecttype.sites.add(self.site)
        objecttype.metatypes.add(self.metatype)
        objecttype.authors.add(self.author)
        return objecttype

    def create_discussions(self, objecttype):
        comment = comments.get_model().objects.create(comment='My Comment',
                                                      user=self.author,
                                                      content_object=objecttype,
                                                      site=self.site)
        pingback = comments.get_model().objects.create(comment='My Pingback',
                                                       user=self.author,
                                                       content_object=objecttype,
                                                       site=self.site)
        pingback.flags.create(user=self.author, flag='pingback')
        trackback = comments.get_model().objects.create(comment='My Trackback',
                                                        user=self.author,
                                                        content_object=objecttype,
                                                        site=self.site)
        trackback.flags.create(user=self.author, flag='trackback')
        return [comment, pingback, trackback]

    def test_objecttype_feed(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        objecttype = self.create_published_objecttype()
        feed = ObjecttypeFeed()
        self.assertEquals(feed.item_pubdate(objecttype), objecttype.creation_date)
        self.assertEquals(feed.item_metatypes(objecttype), [self.metatype.title])
        self.assertEquals(feed.item_author_name(objecttype), self.author.username)
        self.assertEquals(feed.item_author_email(objecttype), self.author.email)
        self.assertEquals(
            feed.item_author_link(objecttype),
            'http://example.com/authors/%s/' % self.author.username)
        # Test a NoReverseMatch for item_author_link
        self.author.username = '[]'
        self.author.save()
        feed.item_author_name(objecttype)
        self.assertEquals(feed.item_author_link(objecttype), 'http://example.com')
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_objecttype_feed_enclosure(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        objecttype = self.create_published_objecttype()
        feed = ObjecttypeFeed()
        self.assertEquals(
            feed.item_enclosure_url(objecttype), 'http://example.com/image.jpg')
        objecttype.content = 'My test content with image <img src="image.jpg" />',
        objecttype.save()
        self.assertEquals(
            feed.item_enclosure_url(objecttype), 'http://example.com/image.jpg')
        objecttype.content = 'My test content with image ' \
                        '<img src="http://test.com/image.jpg" />'
        objecttype.save()
        self.assertEquals(
            feed.item_enclosure_url(objecttype), 'http://test.com/image.jpg')
        objecttype.image = 'image_field.jpg'
        objecttype.save()
        self.assertEquals(feed.item_enclosure_url(objecttype),
                          '%simage_field.jpg' % settings.MEDIA_URL)
        self.assertEquals(feed.item_enclosure_length(objecttype), '100000')
        self.assertEquals(feed.item_enclosure_mime_type(objecttype), 'image/jpeg')
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_latest_objecttypes(self):
        self.create_published_objecttype()
        feed = LatestObjecttypes()
        self.assertEquals(feed.link(), '/')
        self.assertEquals(len(feed.items()), 1)
        self.assertEquals(feed.title(),
                          'example.com - %s' % _('Latest objecttypes'))
        self.assertEquals(
            feed.description(),
            _('The latest objecttypes for the site %s') % 'example.com')

    def test_metatype_objecttypes(self):
        self.create_published_objecttype()
        feed = MetatypeObjecttypes()
        self.assertEquals(feed.get_object('request', '/tests/'), self.metatype)
        self.assertEquals(len(feed.items(self.metatype)), 1)
        self.assertEquals(feed.link(self.metatype), '/metatypes/tests/')
        self.assertEquals(
            feed.title(self.metatype),
            _('Objecttypes for the metatype %s') % self.metatype.title)
        self.assertEquals(
            feed.description(self.metatype),
            _('The latest objecttypes for the metatype %s') % self.metatype.title)

    def test_author_objecttypes(self):
        self.create_published_objecttype()
        feed = AuthorObjecttypes()
        self.assertEquals(feed.get_object('request', 'admin'), self.author)
        self.assertEquals(len(feed.items(self.author)), 1)
        self.assertEquals(feed.link(self.author), '/authors/admin/')
        self.assertEquals(feed.title(self.author),
                          _('Objecttypes for author %s') % self.author.username)
        self.assertEquals(feed.description(self.author),
                          _('The latest objecttypes by %s') % self.author.username)

    def test_tag_objecttypes(self):
        self.create_published_objecttype()
        feed = TagObjecttypes()
        tag = Tag(name='tests')
        self.assertEquals(feed.get_object('request', 'tests').name, 'tests')
        self.assertEquals(len(feed.items('tests')), 1)
        self.assertEquals(feed.link(tag), '/tags/tests/')
        self.assertEquals(feed.title(tag),
                          _('Objecttypes for the tag %s') % tag.name)
        self.assertEquals(feed.description(tag),
                          _('The latest objecttypes for the tag %s') % tag.name)

    def test_search_objecttypes(self):
        class FakeRequest:
            def __init__(self, val):
                self.GET = {'pattern': val}
        self.create_published_objecttype()
        feed = SearchObjecttypes()
        self.assertRaises(ObjectDoesNotExist,
                          feed.get_object, FakeRequest('te'))
        self.assertEquals(feed.get_object(FakeRequest('test')), 'test')
        self.assertEquals(len(feed.items('test')), 1)
        self.assertEquals(feed.link('test'), '/search/?pattern=test')
        self.assertEquals(feed.title('test'),
                          _("Results of the search for '%s'") % 'test')
        self.assertEquals(
            feed.description('test'),
            _("The objecttypes containing the pattern '%s'") % 'test')

    def test_objecttype_discussions(self):
        objecttype = self.create_published_objecttype()
        comments = self.create_discussions(objecttype)
        feed = ObjecttypeDiscussions()
        self.assertEquals(feed.get_object(
            'request', 2010, 1, 1, objecttype.slug), objecttype)
        self.assertEquals(feed.link(objecttype), '/2010/01/01/my-test-objecttype/')
        self.assertEquals(len(feed.items(objecttype)), 3)
        self.assertEquals(feed.item_pubdate(comments[0]),
                          comments[0].submit_date)
        self.assertEquals(feed.item_link(comments[0]),
                          '/comments/cr/%i/1/#c1' % self.objecttype_ct_id)
        self.assertEquals(feed.item_author_name(comments[0]), 'admin')
        self.assertEquals(feed.item_author_email(comments[0]),
                          'admin@example.com')
        self.assertEquals(feed.item_author_link(comments[0]), '')
        self.assertEquals(feed.title(objecttype),
                          _('Discussions on %s') % objecttype.title)
        self.assertEquals(
            feed.description(objecttype),
            _('The latest discussions for the objecttype %s') % objecttype.title)

    def test_objecttype_comments(self):
        objecttype = self.create_published_objecttype()
        comments = self.create_discussions(objecttype)
        feed = ObjecttypeComments()
        self.assertEquals(list(feed.items(objecttype)), [comments[0]])
        self.assertEquals(feed.item_link(comments[0]),
                          '/comments/cr/%i/1/#comment_1' % self.objecttype_ct_id)
        self.assertEquals(feed.title(objecttype),
                          _('Comments on %s') % objecttype.title)
        self.assertEquals(
            feed.description(objecttype),
            _('The latest comments for the objecttype %s') % objecttype.title)
        self.assertEquals(
            feed.item_enclosure_url(comments[0]),
            'http://www.gravatar.com/avatar/e64c7d89f26b'
            'd1972efa854d13d7dd61.jpg?s=80&amp;r=g')
        self.assertEquals(feed.item_enclosure_length(objecttype), '100000')
        self.assertEquals(feed.item_enclosure_mime_type(objecttype), 'image/jpeg')

    def test_objecttype_pingbacks(self):
        objecttype = self.create_published_objecttype()
        comments = self.create_discussions(objecttype)
        feed = ObjecttypePingbacks()
        self.assertEquals(list(feed.items(objecttype)), [comments[1]])
        self.assertEquals(feed.item_link(comments[1]),
                          '/comments/cr/%i/1/#pingback_2' % self.objecttype_ct_id)
        self.assertEquals(feed.title(objecttype),
                          _('Pingbacks on %s') % objecttype.title)
        self.assertEquals(
            feed.description(objecttype),
            _('The latest pingbacks for the objecttype %s') % objecttype.title)

    def test_objecttype_trackbacks(self):
        objecttype = self.create_published_objecttype()
        comments = self.create_discussions(objecttype)
        feed = ObjecttypeTrackbacks()
        self.assertEquals(list(feed.items(objecttype)), [comments[2]])
        self.assertEquals(feed.item_link(comments[2]),
                          '/comments/cr/%i/1/#trackback_3' % self.objecttype_ct_id)
        self.assertEquals(feed.title(objecttype),
                          _('Trackbacks on %s') % objecttype.title)
        self.assertEquals(
            feed.description(objecttype),
            _('The latest trackbacks for the objecttype %s') % objecttype.title)

    def test_objecttype_feed_no_authors(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        objecttype = self.create_published_objecttype()
        objecttype.authors.clear()
        feed = ObjecttypeFeed()
        self.assertEquals(feed.item_author_name(objecttype), None)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_objecttype_feed_rss_or_atom(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        feed = LatestObjecttypes()
        self.assertEquals(feed.feed_type, DefaultFeed)
        feeds.FEEDS_FORMAT = 'atom'
        feed = LatestObjecttypes()
        self.assertEquals(feed.feed_type, Atom1Feed)
        self.assertEquals(feed.subtitle, feed.description)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_discussion_feed_with_same_slugs(self):
        """
        https://github.com/gnowgi/django-gstudio/issues/104

        OK, Here I will reproduce the original case: getting a discussion
        type feed, with a same slug.

        The correction of this case, will need some changes in the
        get_object method.
        """
        objecttype = self.create_published_objecttype()

        feed = ObjecttypeDiscussions()
        self.assertEquals(feed.get_object(
            'request', 2010, 1, 1, objecttype.slug), objecttype)

        params = {'title': 'My test objecttype, part II',
                  'content': 'My content ',
                  'slug': 'my-test-objecttype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 2, 1),
                  'status': PUBLISHED}
        objecttype_same_slug = Objecttype.objects.create(**params)
        objecttype_same_slug.sites.add(self.site)
        objecttype_same_slug.authors.add(self.author)

        self.assertEquals(feed.get_object(
            'request', 2010, 2, 1, objecttype_same_slug.slug), objecttype_same_slug)
