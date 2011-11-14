"""Test cases for Relationapp's feeds"""
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

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.managers import PUBLISHED
from relationapp import feeds
from relationapp.feeds import RelationtypeFeed
from relationapp.feeds import LatestRelationtypes
from relationapp.feeds import RelationRelationtypes
from relationapp.feeds import AuthorRelationtypes
from relationapp.feeds import TagRelationtypes
from relationapp.feeds import SearchRelationtypes
from relationapp.feeds import RelationtypeDiscussions
from relationapp.feeds import RelationtypeComments
from relationapp.feeds import RelationtypePingbacks
from relationapp.feeds import RelationtypeTrackbacks


class RelationappFeedsTestCase(TestCase):
    """Test cases for the Feed classes provided"""
    urls = 'relationapp.tests.urls'

    def setUp(self):
        self.site = Site.objects.get_current()
        self.author = User.objects.create(username='admin',
                                          email='admin@example.com')
        self.relation = Relation.objects.create(title='Tests', slug='tests')
        self.relationtype_ct_id = ContentType.objects.get_for_model(Relationtype).pk

    def create_published_relationtype(self):
        params = {'title': 'My test relationtype',
                  'content': 'My test content with image '
                  '<img src="/image.jpg" />',
                  'slug': 'my-test-relationtype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 1, 1),
                  'status': PUBLISHED}
        relationtype = Relationtype.objects.create(**params)
        relationtype.sites.add(self.site)
        relationtype.relations.add(self.relation)
        relationtype.authors.add(self.author)
        return relationtype

    def create_discussions(self, relationtype):
        comment = comments.get_model().objects.create(comment='My Comment',
                                                      user=self.author,
                                                      content_object=relationtype,
                                                      site=self.site)
        pingback = comments.get_model().objects.create(comment='My Pingback',
                                                       user=self.author,
                                                       content_object=relationtype,
                                                       site=self.site)
        pingback.flags.create(user=self.author, flag='pingback')
        trackback = comments.get_model().objects.create(comment='My Trackback',
                                                        user=self.author,
                                                        content_object=relationtype,
                                                        site=self.site)
        trackback.flags.create(user=self.author, flag='trackback')
        return [comment, pingback, trackback]

    def test_relationtype_feed(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        relationtype = self.create_published_relationtype()
        feed = RelationtypeFeed()
        self.assertEquals(feed.item_pubdate(relationtype), relationtype.creation_date)
        self.assertEquals(feed.item_relations(relationtype), [self.relation.title])
        self.assertEquals(feed.item_author_name(relationtype), self.author.username)
        self.assertEquals(feed.item_author_email(relationtype), self.author.email)
        self.assertEquals(
            feed.item_author_link(relationtype),
            'http://example.com/authors/%s/' % self.author.username)
        # Test a NoReverseMatch for item_author_link
        self.author.username = '[]'
        self.author.save()
        feed.item_author_name(relationtype)
        self.assertEquals(feed.item_author_link(relationtype), 'http://example.com')
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_relationtype_feed_enclosure(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        relationtype = self.create_published_relationtype()
        feed = RelationtypeFeed()
        self.assertEquals(
            feed.item_enclosure_url(relationtype), 'http://example.com/image.jpg')
        relationtype.content = 'My test content with image <img src="image.jpg" />',
        relationtype.save()
        self.assertEquals(
            feed.item_enclosure_url(relationtype), 'http://example.com/image.jpg')
        relationtype.content = 'My test content with image ' \
                        '<img src="http://test.com/image.jpg" />'
        relationtype.save()
        self.assertEquals(
            feed.item_enclosure_url(relationtype), 'http://test.com/image.jpg')
        relationtype.image = 'image_field.jpg'
        relationtype.save()
        self.assertEquals(feed.item_enclosure_url(relationtype),
                          '%simage_field.jpg' % settings.MEDIA_URL)
        self.assertEquals(feed.item_enclosure_length(relationtype), '100000')
        self.assertEquals(feed.item_enclosure_mime_type(relationtype), 'image/jpeg')
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_latest_relationtypes(self):
        self.create_published_relationtype()
        feed = LatestRelationtypes()
        self.assertEquals(feed.link(), '/')
        self.assertEquals(len(feed.items()), 1)
        self.assertEquals(feed.title(),
                          'example.com - %s' % _('Latest relationtypes'))
        self.assertEquals(
            feed.description(),
            _('The latest relationtypes for the site %s') % 'example.com')

    def test_relation_relationtypes(self):
        self.create_published_relationtype()
        feed = RelationRelationtypes()
        self.assertEquals(feed.get_object('request', '/tests/'), self.relation)
        self.assertEquals(len(feed.items(self.relation)), 1)
        self.assertEquals(feed.link(self.relation), '/relations/tests/')
        self.assertEquals(
            feed.title(self.relation),
            _('Relationtypes for the relation %s') % self.relation.title)
        self.assertEquals(
            feed.description(self.relation),
            _('The latest relationtypes for the relation %s') % self.relation.title)

    def test_author_relationtypes(self):
        self.create_published_relationtype()
        feed = AuthorRelationtypes()
        self.assertEquals(feed.get_object('request', 'admin'), self.author)
        self.assertEquals(len(feed.items(self.author)), 1)
        self.assertEquals(feed.link(self.author), '/authors/admin/')
        self.assertEquals(feed.title(self.author),
                          _('Relationtypes for author %s') % self.author.username)
        self.assertEquals(feed.description(self.author),
                          _('The latest relationtypes by %s') % self.author.username)

    def test_tag_relationtypes(self):
        self.create_published_relationtype()
        feed = TagRelationtypes()
        tag = Tag(name='tests')
        self.assertEquals(feed.get_object('request', 'tests').name, 'tests')
        self.assertEquals(len(feed.items('tests')), 1)
        self.assertEquals(feed.link(tag), '/tags/tests/')
        self.assertEquals(feed.title(tag),
                          _('Relationtypes for the tag %s') % tag.name)
        self.assertEquals(feed.description(tag),
                          _('The latest relationtypes for the tag %s') % tag.name)

    def test_search_relationtypes(self):
        class FakeRequest:
            def __init__(self, val):
                self.GET = {'pattern': val}
        self.create_published_relationtype()
        feed = SearchRelationtypes()
        self.assertRaises(ObjectDoesNotExist,
                          feed.get_object, FakeRequest('te'))
        self.assertEquals(feed.get_object(FakeRequest('test')), 'test')
        self.assertEquals(len(feed.items('test')), 1)
        self.assertEquals(feed.link('test'), '/search/?pattern=test')
        self.assertEquals(feed.title('test'),
                          _("Results of the search for '%s'") % 'test')
        self.assertEquals(
            feed.description('test'),
            _("The relationtypes containing the pattern '%s'") % 'test')

    def test_relationtype_discussions(self):
        relationtype = self.create_published_relationtype()
        comments = self.create_discussions(relationtype)
        feed = RelationtypeDiscussions()
        self.assertEquals(feed.get_object(
            'request', 2010, 1, 1, relationtype.slug), relationtype)
        self.assertEquals(feed.link(relationtype), '/2010/01/01/my-test-relationtype/')
        self.assertEquals(len(feed.items(relationtype)), 3)
        self.assertEquals(feed.item_pubdate(comments[0]),
                          comments[0].submit_date)
        self.assertEquals(feed.item_link(comments[0]),
                          '/comments/cr/%i/1/#c1' % self.relationtype_ct_id)
        self.assertEquals(feed.item_author_name(comments[0]), 'admin')
        self.assertEquals(feed.item_author_email(comments[0]),
                          'admin@example.com')
        self.assertEquals(feed.item_author_link(comments[0]), '')
        self.assertEquals(feed.title(relationtype),
                          _('Discussions on %s') % relationtype.title)
        self.assertEquals(
            feed.description(relationtype),
            _('The latest discussions for the relationtype %s') % relationtype.title)

    def test_relationtype_comments(self):
        relationtype = self.create_published_relationtype()
        comments = self.create_discussions(relationtype)
        feed = RelationtypeComments()
        self.assertEquals(list(feed.items(relationtype)), [comments[0]])
        self.assertEquals(feed.item_link(comments[0]),
                          '/comments/cr/%i/1/#comment_1' % self.relationtype_ct_id)
        self.assertEquals(feed.title(relationtype),
                          _('Comments on %s') % relationtype.title)
        self.assertEquals(
            feed.description(relationtype),
            _('The latest comments for the relationtype %s') % relationtype.title)
        self.assertEquals(
            feed.item_enclosure_url(comments[0]),
            'http://www.gravatar.com/avatar/e64c7d89f26b'
            'd1972efa854d13d7dd61.jpg?s=80&amp;r=g')
        self.assertEquals(feed.item_enclosure_length(relationtype), '100000')
        self.assertEquals(feed.item_enclosure_mime_type(relationtype), 'image/jpeg')

    def test_relationtype_pingbacks(self):
        relationtype = self.create_published_relationtype()
        comments = self.create_discussions(relationtype)
        feed = RelationtypePingbacks()
        self.assertEquals(list(feed.items(relationtype)), [comments[1]])
        self.assertEquals(feed.item_link(comments[1]),
                          '/comments/cr/%i/1/#pingback_2' % self.relationtype_ct_id)
        self.assertEquals(feed.title(relationtype),
                          _('Pingbacks on %s') % relationtype.title)
        self.assertEquals(
            feed.description(relationtype),
            _('The latest pingbacks for the relationtype %s') % relationtype.title)

    def test_relationtype_trackbacks(self):
        relationtype = self.create_published_relationtype()
        comments = self.create_discussions(relationtype)
        feed = RelationtypeTrackbacks()
        self.assertEquals(list(feed.items(relationtype)), [comments[2]])
        self.assertEquals(feed.item_link(comments[2]),
                          '/comments/cr/%i/1/#trackback_3' % self.relationtype_ct_id)
        self.assertEquals(feed.title(relationtype),
                          _('Trackbacks on %s') % relationtype.title)
        self.assertEquals(
            feed.description(relationtype),
            _('The latest trackbacks for the relationtype %s') % relationtype.title)

    def test_relationtype_feed_no_authors(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        relationtype = self.create_published_relationtype()
        relationtype.authors.clear()
        feed = RelationtypeFeed()
        self.assertEquals(feed.item_author_name(relationtype), None)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_relationtype_feed_rss_or_atom(self):
        original_feeds_format = feeds.FEEDS_FORMAT
        feeds.FEEDS_FORMAT = ''
        feed = LatestRelationtypes()
        self.assertEquals(feed.feed_type, DefaultFeed)
        feeds.FEEDS_FORMAT = 'atom'
        feed = LatestRelationtypes()
        self.assertEquals(feed.feed_type, Atom1Feed)
        self.assertEquals(feed.subtitle, feed.description)
        feeds.FEEDS_FORMAT = original_feeds_format

    def test_discussion_feed_with_same_slugs(self):
        """
        https://github.com/gnowgi/django-relationapp/issues/104

        OK, Here I will reproduce the original case: getting a discussion
        type feed, with a same slug.

        The correction of this case, will need some changes in the
        get_object method.
        """
        relationtype = self.create_published_relationtype()

        feed = RelationtypeDiscussions()
        self.assertEquals(feed.get_object(
            'request', 2010, 1, 1, relationtype.slug), relationtype)

        params = {'title': 'My test relationtype, part II',
                  'content': 'My content ',
                  'slug': 'my-test-relationtype',
                  'tags': 'tests',
                  'creation_date': datetime(2010, 2, 1),
                  'status': PUBLISHED}
        relationtype_same_slug = Relationtype.objects.create(**params)
        relationtype_same_slug.sites.add(self.site)
        relationtype_same_slug.authors.add(self.author)

        self.assertEquals(feed.get_object(
            'request', 2010, 2, 1, relationtype_same_slug.slug), relationtype_same_slug)
