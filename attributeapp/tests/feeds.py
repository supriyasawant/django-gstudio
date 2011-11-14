"""Test cases for Attributeapp's feeds"""
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

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.managers import PUBLISHED
from attributeapp import feeds
from attributeapp.feeds import AttributetypeFeed
from attributeapp.feeds import LatestAttributetypes
from attributeapp.feeds import AttributeAttributetypes
from attributeapp.feeds import AuthorAttributetypes
from attributeapp.feeds import TagAttributetypes
from attributeapp.feeds import SearchAttributetypes
from attributeapp.feeds import AttributetypeDiscussions
from attributeapp.feeds import AttributetypeComments
from attributeapp.feeds import AttributetypePingbacks
from attributeapp.feeds import AttributetypeTrackbacks


class AttributeappFeedsTestCase(TestCase):
    """Test cases for the Feed classes provided"""
    urls = 'attributeapp.tests.urls'

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.attribute = Attribute.objects.create(title='Tests', slug='tests')
        self.attributetype_ct_id = ContentType.objects.get_for_model(Attributetype).pk

    def create_published_attributetype(self):
        params = {'title': 'My test attributetype',
                  'content': 'My test content with image '
                  '<img src="/image.jpg" />',
                  'slug': 'my-test-attributetype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        attributetype = Attributetype.objects.create(**params)
        attributetype.sites.add(self.site)
        attributetype.attributes.add(self.attribute)
        attributetype.authors.add(self.author)
        return attributetype

    def create_discussions(self, attributetype):
        comment = comments.get_model().objects.create(comment='My Comment',
                                                      user=self.author,
                                                      content_object=attributetype,
                                                      site=self.site)
        pingback = comments.get_model().objects.create(comment='My Pingback',
                                                       user=self.author,
                                                       content_object=attributetype,
                                                       site=self.site)
        pingback.flags.create(user=self.author, flag='pingback')
        trackback = comments.get_model().objects.create(comment='My Trackback',
                                                        user=self.author,
                                                        content_object=attributetype,
                                                        site=self.site)
        trackback.flags.create(user=self.author, flag='trackback')
        return [comment, pingback, trackback]

    def test_attributetype_feed(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        attributetype = self.create_published_attributetype()
        feed = AttributetypeFeed()
        self.assertEquals(feed.item_pubdate(attributetype), attributetype.creation_date)
        self.assertEquals(feed.item_attributes(attributetype), [self.attribute.title])
        self.assertEquals(feed.item_author_name(attributetype), self.author.username)
        self.assertEquals(feed.item_author_email(attributetype), self.author.email)
        self.assertEquals(
            feed.item_author_link(attributetype),
            'http://example.com/authors/%s/' % self.author.username)
        # Test a NoReverseMatch for item_author_link
        self.author.username = '[]'
        self.author.save()
        feed.item_author_name(attributetype)
        self.assertEquals(feed.item_author_link(attributetype), 'http://example.com')
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_attributetype_feed_enclosure(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        attributetype = self.create_published_attributetype()
        feed = AttributetypeFeed()
        self.assertEquals(
            feed.item_enclosure_url(attributetype), 'http://example.com/image.jpg')
        attributetype.content = 'My test content with image <img src="image.jpg" />',
        attributetype.save()
        self.assertEquals(
            feed.item_enclosure_url(attributetype), 'http://example.com/image.jpg')
        attributetype.content = 'My test content with image ' \
                        '<img src="http://test.com/image.jpg" />'
        attributetype.save()
        self.assertEquals(
            feed.item_enclosure_url(attributetype), 'http://test.com/image.jpg')
        attributetype.image = 'image_field.jpg'
        attributetype.save()
        self.assertEquals(feed.item_enclosure_url(attributetype),
                          '%simage_field.jpg' % settings.MEDIA_URL)
        self.assertEquals(feed.item_enclosure_length(attributetype), '100000')
        self.assertEquals(feed.item_enclosure_mime_type(attributetype), 'image/jpeg')
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_latest_attributetypes(self):
        self.create_published_attributetype()
        feed = LatestAttributetypes()
        self.assertEquals(feed.link(), '/')
        self.assertEquals(len(feed.items()), 1)
        self.assertEquals(feed.title(),
                          'example.com - %s' % _('Latest attributetypes'))
        self.assertEquals(
            feed.description(),
            _('The latest attributetypes for the site %s') % 'example.com')

    def test_attribute_attributetypes(self):
        self.create_published_attributetype()
        feed = AttributeAttributetypes()
        self.assertEquals(feed.get_object('request', '/tests/'), self.attribute)
        self.assertEquals(len(feed.items(self.attribute)), 1)
        self.assertEquals(feed.link(self.attribute), '/attributes/tests/')
        self.assertEquals(
            feed.title(self.attribute),
            _('Attributetypes for the attribute %s') % self.attribute.title)
        self.assertEquals(
            feed.description(self.attribute),
            _('The latest attributetypes for the attribute %s') % self.attribute.title)

    def test_author_attributetypes(self):
        self.create_published_attributetype()
        feed = AuthorAttributetypes()
        self.assertEquals(feed.get_object('request', 'admin'), self.author)
        self.assertEquals(len(feed.items(self.author)), 1)
        self.assertEquals(feed.link(self.author), '/authors/admin/')
        self.assertEquals(feed.title(self.author),
                          _('Attributetypes for author %s') % self.author.username)
        self.assertEquals(feed.description(self.author),
                          _('The latest attributetypes by %s') % self.author.username)

    def test_tag_attributetypes(self):
        self.create_published_attributetype()
        feed = TagAttributetypes()
        tag = Tag(name='tests')
        self.assertEquals(feed.get_object('request', 'tests').name, 'tests')
        self.assertEquals(len(feed.items('tests')), 1)
        self.assertEquals(feed.link(tag), '/tags/tests/')
        self.assertEquals(feed.title(tag),
                          _('Attributetypes for the tag %s') % tag.name)
        self.assertEquals(feed.description(tag),
                          _('The latest attributetypes for the tag %s') % tag.name)

    def test_search_attributetypes(self):
        class FakeRequest:
            def __init__(self, val):
                self.GET = {'pattern': val}
        self.create_published_attributetype()
        feed = SearchAttributetypes()
        self.assertRaises(ObjectDoesNotExist,
                          feed.get_object, FakeRequest('te'))
        self.assertEquals(feed.get_object(FakeRequest('test')), 'test')
        self.assertEquals(len(feed.items('test')), 1)
        self.assertEquals(feed.link('test'), '/search/?pattern=test')
        self.assertEquals(feed.title('test'),
                          _("Results of the search for '%s'") % 'test')
        self.assertEquals(
            feed.description('test'),
            _("The attributetypes containing the pattern '%s'") % 'test')

    def test_attributetype_discussions(self):
        attributetype = self.create_published_attributetype()
        comments = self.create_discussions(attributetype)
        feed = AttributetypeDiscussions()
        self.assertEquals(feed.get_object(
            'request', 2010, 1, 1, attributetype.slug), attributetype)
        self.assertEquals(feed.link(attributetype), '/2010/01/01/my-test-attributetype/')
        self.assertEquals(len(feed.items(attributetype)), 3)
        self.assertEquals(feed.item_pubdate(comments[0]),
                          comments[0].submit_date)
        self.assertEquals(feed.item_link(comments[0]),
                          '/comments/cr/%i/1/#c1' % self.attributetype_ct_id)
        self.assertEquals(feed.item_author_name(comments[0]), 'admin')
        self.assertEquals(feed.item_author_email(comments[0]),
                          'admin@example.com')
        self.assertEquals(feed.item_author_link(comments[0]), '')
        self.assertEquals(feed.title(attributetype),
                          _('Discussions on %s') % attributetype.title)
        self.assertEquals(
            feed.description(attributetype),
            _('The latest discussions for the attributetype %s') % attributetype.title)

    def test_attributetype_comments(self):
        attributetype = self.create_published_attributetype()
        comments = self.create_discussions(attributetype)
        feed = AttributetypeComments()
        self.assertEquals(list(feed.items(attributetype)), [comments[0]])
        self.assertEquals(feed.item_link(comments[0]),
                          '/comments/cr/%i/1/#comment_1' % self.attributetype_ct_id)
        self.assertEquals(feed.title(attributetype),
                          _('Comments on %s') % attributetype.title)
        self.assertEquals(
            feed.description(attributetype),
            _('The latest comments for the attributetype %s') % attributetype.title)
        self.assertEquals(
            feed.item_enclosure_url(comments[0]),
            'http://www.gravatar.com/avatar/e64c7d89f26b'
            'd1972efa854d13d7dd61.jpg?s=80&amp;r=g')
        self.assertEquals(feed.item_enclosure_length(attributetype), '100000')
        self.assertEquals(feed.item_enclosure_mime_type(attributetype), 'image/jpeg')

    def test_attributetype_pingbacks(self):
        attributetype = self.create_published_attributetype()
        comments = self.create_discussions(attributetype)
        feed = AttributetypePingbacks()
        self.assertEquals(list(feed.items(attributetype)), [comments[1]])
        self.assertEquals(feed.item_link(comments[1]),
                          '/comments/cr/%i/1/#pingback_2' % self.attributetype_ct_id)
        self.assertEquals(feed.title(attributetype),
                          _('Pingbacks on %s') % attributetype.title)
        self.assertEquals(
            feed.description(attributetype),
            _('The latest pingbacks for the attributetype %s') % attributetype.title)

    def test_attributetype_trackbacks(self):
        attributetype = self.create_published_attributetype()
        comments = self.create_discussions(attributetype)
        feed = AttributetypeTrackbacks()
        self.assertEquals(list(feed.items(attributetype)), [comments[2]])
        self.assertEquals(feed.item_link(comments[2]),
                          '/comments/cr/%i/1/#trackback_3' % self.attributetype_ct_id)
        self.assertEquals(feed.title(attributetype),
                          _('Trackbacks on %s') % attributetype.title)
        self.assertEquals(
            feed.description(attributetype),
            _('The latest trackbacks for the attributetype %s') % attributetype.title)

    def test_attributetype_feed_no_authors(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        attributetype = self.create_published_attributetype()
        attributetype.authors.clear()
        feed = AttributetypeFeed()
        self.assertEquals(feed.item_author_name(attributetype), None)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_attributetype_feed_rss_or_atom(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        feed = LatestAttributetypes()
        self.assertEquals(feed.feed_type, DefaultFeed)
        feeds.FEEDS_FORMAT = 'atom'
        feed = LatestAttributetypes()
        self.assertEquals(feed.feed_type, Atom1Feed)
        self.assertEquals(feed.subtitle, feed.description)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_discussion_feed_with_same_slugs(self):
        """
        https://github.com/gnowgi/django-attributeapp/issues/104

        OK, Here I will reproduce the original case: getting a discussion
        type feed, with a same slug.

        The correction of this case, will need some changes in the
        get_object method.
        """
        attributetype = self.create_published_attributetype()

        feed = AttributetypeDiscussions()
        self.assertEquals(feed.get_object(
            'request', 2010, 1, 1, attributetype.slug), attributetype)

        params = {'title': 'My test attributetype, part II',
                  'content': 'My content ',
                  'slug': 'my-test-attributetype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 2, 1),
                  'status': PUBLISHED}
        attributetype_same_slug = Attributetype.objects.create(**params)
        attributetype_same_slug.sites.add(self.site)
        attributetype_same_slug.authors.add(self.author)

        self.assertEquals(feed.get_object(
            'request', 2010, 2, 1, attributetype_same_slug.slug), attributetype_same_slug)
