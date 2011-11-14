"""Feeds for Objectapp"""
from urlparse import urljoin
from BeautifulSoup import BeautifulSoup

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.utils.translation import ugettext as _
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import NoReverseMatch
from django.core.exceptions import ObjectDoesNotExist

from tagging.models import Tag
from tagging.models import TaggedItem

from objectapp.models import GBObject
from objectapp.settings import COPYRIGHT
from objectapp.settings import PROTOCOL
from objectapp.settings import FEEDS_FORMAT
from objectapp.settings import FEEDS_MAX_ITEMS
from objectapp.managers import gbobjects_published
from objectapp.views.objecttypes import get_objecttype_or_404
from objectapp.templatetags.objectapp_tags import get_gravatar


class ObjectappFeed(Feed):
    """Base Feed for Objectapp"""
    feed_copyright = COPYRIGHT

    def __init__(self):
        self.site = Site.objects.get_current()
        self.site_url = '%s://%s' % (PROTOCOL, self.site.domain)
        if FEEDS_FORMAT == 'atom':
            self.feed_type = Atom1Feed
            self.subtitle = self.description


class GBObjectFeed(ObjectappFeed):
    """Base GBObject Feed"""
    title_template = 'feeds/gbobject_title.html'
    description_template = 'feeds/gbobject_description.html'

    def item_pubdate(self, item):
        """Publication date of an gbobject"""
        return item.creation_date

    def item_objecttypes(self, item):
        """GBObject's objecttypes"""
        return [objecttype.title for objecttype in item.objecttypes.all()]

    def item_author_name(self, item):
        """Returns the first author of an gbobject"""
        if item.authors.count():
            self.item_author = item.authors.all()[0]
            return self.item_author.username

    def item_author_email(self, item):
        """Returns the first author's email"""
        return self.item_author.email

    def item_author_link(self, item):
        """Returns the author's URL"""
        try:
            author_url = reverse('objectapp_author_detail',
                                 args=[self.item_author.username])
            return self.site_url + author_url
        except NoReverseMatch:
            return self.site_url

    def item_enclosure_url(self, item):
        """Returns an image for enclosure"""
        if item.image:
            return item.image.url

        img = BeautifulSoup(item.html_content).find('img')
        if img:
            return urljoin(self.site_url, img['src'])

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class LatestGBObjects(GBObjectFeed):
    """Feed for the latest gbobjects"""

    def link(self):
        """URL of latest gbobjects"""
        return reverse('objectapp_gbobject_archive_index')

    def items(self):
        """Items are published gbobjects"""
        return GBObject.published.all()[:FEEDS_MAX_ITEMS]

    def title(self):
        """Title of the feed"""
        return '%s - %s' % (self.site.name, _('Latest gbobjects'))

    def description(self):
        """Description of the feed"""
        return _('The latest gbobjects for the site %s') % self.site.name


class ObjecttypeGBObjects(GBObjectFeed):
    """Feed filtered by a objecttype"""

    def get_object(self, request, path):
        """Retrieve the objecttype by his path"""
        return get_objecttype_or_404(path)

    def items(self, obj):
        """Items are the published gbobjects of the objecttype"""
        return obj.gbobjects_published()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the objecttype"""
        return obj.get_absolute_url()

    def title(self, obj):
        """Title of the feed"""
        return _('GBObjects for the objecttype %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest gbobjects for the objecttype %s') % obj.title


class AuthorGBObjects(GBObjectFeed):
    """Feed filtered by an author"""

    def get_object(self, request, username):
        """Retrieve the author by his username"""
        return get_object_or_404(User, username=username)

    def items(self, obj):
        """Items are the published gbobjects of the author"""
        return gbobjects_published(obj.gbobjects)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the author"""
        return reverse('objectapp_author_detail', args=[obj.username])

    def title(self, obj):
        """Title of the feed"""
        return _('GBObjects for author %s') % obj.username

    def description(self, obj):
        """Description of the feed"""
        return _('The latest gbobjects by %s') % obj.username


class TagGBObjects(GBObjectFeed):
    """Feed filtered by a tag"""

    def get_object(self, request, slug):
        """Retrieve the tag by his name"""
        return get_object_or_404(Tag, name=slug)

    def items(self, obj):
        """Items are the published gbobjects of the tag"""
        return TaggedItem.objects.get_by_model(
            GBObject.published.all(), obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the tag"""
        return reverse('objectapp_tag_detail', args=[obj.name])

    def title(self, obj):
        """Title of the feed"""
        return _('GBObjects for the tag %s') % obj.name

    def description(self, obj):
        """Description of the feed"""
        return _('The latest gbobjects for the tag %s') % obj.name


class SearchGBObjects(GBObjectFeed):
    """Feed filtered by a search pattern"""

    def get_object(self, request):
        """The GET parameter 'pattern' is the object"""
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            raise ObjectDoesNotExist
        return pattern

    def items(self, obj):
        """Items are the published gbobjects founds"""
        return GBObject.published.search(obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the search request"""
        return '%s?pattern=%s' % (reverse('objectapp_gbobject_search'), obj)

    def title(self, obj):
        """Title of the feed"""
        return _("Results of the search for '%s'") % obj

    def description(self, obj):
        """Description of the feed"""
        return _("The gbobjects containing the pattern '%s'") % obj


class GBObjectDiscussions(ObjectappFeed):
    """Feed for discussions in an gbobject"""
    title_template = 'feeds/discussion_title.html'
    description_template = 'feeds/discussion_description.html'

    def get_object(self, request, year, month, day, slug):
        """Retrieve the discussions by gbobject's slug"""
        return get_object_or_404(GBObject.published, slug=slug,
                                 creation_date__year=year,
                                 creation_date__month=month,
                                 creation_date__day=day)

    def items(self, obj):
        """Items are the discussions on the gbobject"""
        return obj.discussions[:FEEDS_MAX_ITEMS]

    def item_pubdate(self, item):
        """Publication date of a discussion"""
        return item.submit_date

    def item_link(self, item):
        """URL of the discussion"""
        return item.get_absolute_url()

    def link(self, obj):
        """URL of the gbobject"""
        return obj.get_absolute_url()

    def item_author_name(self, item):
        """Author of the discussion"""
        return item.userinfo['name']

    def item_author_email(self, item):
        """Author's email of the discussion"""
        return item.userinfo['email']

    def item_author_link(self, item):
        """Author's URL of the discussion"""
        return item.userinfo['url']

    def title(self, obj):
        """Title of the feed"""
        return _('Discussions on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest discussions for the gbobject %s') % obj.title


class GBObjectComments(GBObjectDiscussions):
    """Feed for comments in an gbobject"""
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    def items(self, obj):
        """Items are the comments on the gbobject"""
        return obj.comments[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the comment"""
        return item.get_absolute_url('#comment_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Comments on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest comments for the gbobject %s') % obj.title

    def item_enclosure_url(self, item):
        """Returns a gravatar image for enclosure"""
        return get_gravatar(item.userinfo['email'])

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class GBObjectPingbacks(GBObjectDiscussions):
    """Feed for pingbacks in an gbobject"""
    title_template = 'feeds/pingback_title.html'
    description_template = 'feeds/pingback_description.html'

    def items(self, obj):
        """Items are the pingbacks on the gbobject"""
        return obj.pingbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the pingback"""
        return item.get_absolute_url('#pingback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Pingbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest pingbacks for the gbobject %s') % obj.title


class GBObjectTrackbacks(GBObjectDiscussions):
    """Feed for trackbacks in an gbobject"""
    title_template = 'feeds/trackback_title.html'
    description_template = 'feeds/trackback_description.html'

    def items(self, obj):
        """Items are the trackbacks on the gbobject"""
        return obj.trackbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the trackback"""
        return item.get_absolute_url('#trackback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Trackbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest trackbacks for the gbobject %s') % obj.title
