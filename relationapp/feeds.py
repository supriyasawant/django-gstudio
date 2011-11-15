"""Feeds for Relationapp"""
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

from relationapp.models import Relationtype
from relationapp.settings import COPYRIGHT
from relationapp.settings import PROTOCOL
from relationapp.settings import FEEDS_FORMAT
from relationapp.settings import FEEDS_MAX_ITEMS
from relationapp.managers import relationtypes_published
from relationapp.views.relations import get_relation_or_404
from relationapp.templatetags.relationapp_tags import get_gravatar


class RelationappFeed(Feed):
    """Base Feed for Relationapp"""
    feed_copyright = COPYRIGHT

    def __init__(self):
        self.site = Site.objects.get_current()
        self.site_url = '%s://%s' % (PROTOCOL, self.site.domain)
        if FEEDS_FORMAT == 'atom':
            self.feed_type = Atom1Feed
            self.subtitle = self.description


class RelationtypeFeed(RelationappFeed):
    """Base Relationtype Feed"""
    title_template = 'feeds/relationtype_title.html'
    description_template = 'feeds/relationtype_description.html'

    def item_pubdate(self, item):
        """Publication date of an relationtype"""
        return item.creation_date

    def item_relations(self, item):
        """Relationtype's relations"""
        return [relation.title for relation in item.relations.all()]

    def item_author_name(self, item):
        """Returns the first author of an relationtype"""
        if item.authors.count():
            self.item_author = item.authors.all()[0]
            return self.item_author.username

    def item_author_email(self, item):
        """Returns the first author's email"""
        return self.item_author.email

    def item_author_link(self, item):
        """Returns the author's URL"""
        try:
            author_url = reverse('relationapp_author_detail',
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


class LatestRelationtypes(RelationtypeFeed):
    """Feed for the latest relationtypes"""

    def link(self):
        """URL of latest relationtypes"""
        return reverse('relationapp_relationtype_archive_index')

    def items(self):
        """Items are published relationtypes"""
        return Relationtype.published.all()[:FEEDS_MAX_ITEMS]

    def title(self):
        """Title of the feed"""
        return '%s - %s' % (self.site.name, _('Latest relationtypes'))

    def description(self):
        """Description of the feed"""
        return _('The latest relationtypes for the site %s') % self.site.name


class RelationRelationtypes(RelationtypeFeed):
    """Feed filtered by a relation"""

    def get_object(self, request, path):
        """Retrieve the relation by his path"""
        return get_relation_or_404(path)

    def items(self, obj):
        """Items are the published relationtypes of the relation"""
        return obj.relationtypes_published()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the relation"""
        return obj.get_absolute_url()

    def title(self, obj):
        """Title of the feed"""
        return _('Relationtypes for the relation %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest relationtypes for the relation %s') % obj.title


class AuthorRelationtypes(RelationtypeFeed):
    """Feed filtered by an author"""

    def get_object(self, request, username):
        """Retrieve the author by his username"""
        return get_object_or_404(User, username=username)

    def items(self, obj):
        """Items are the published relationtypes of the author"""
        return relationtypes_published(obj.relationtypes)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the author"""
        return reverse('relationapp_author_detail', args=[obj.username])

    def title(self, obj):
        """Title of the feed"""
        return _('Relationtypes for author %s') % obj.username

    def description(self, obj):
        """Description of the feed"""
        return _('The latest relationtypes by %s') % obj.username


class TagRelationtypes(RelationtypeFeed):
    """Feed filtered by a tag"""

    def get_object(self, request, slug):
        """Retrieve the tag by his name"""
        return get_object_or_404(Tag, name=slug)

    def items(self, obj):
        """Items are the published relationtypes of the tag"""
        return TaggedItem.objects.get_by_model(
            Relationtype.published.all(), obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the tag"""
        return reverse('relationapp_tag_detail', args=[obj.name])

    def title(self, obj):
        """Title of the feed"""
        return _('Relationtypes for the tag %s') % obj.name

    def description(self, obj):
        """Description of the feed"""
        return _('The latest relationtypes for the tag %s') % obj.name


class SearchRelationtypes(RelationtypeFeed):
    """Feed filtered by a search pattern"""

    def get_object(self, request):
        """The GET parameter 'pattern' is the object"""
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            raise ObjectDoesNotExist
        return pattern

    def items(self, obj):
        """Items are the published relationtypes founds"""
        return Relationtype.published.search(obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the search request"""
        return '%s?pattern=%s' % (reverse('relationapp_relationtype_search'), obj)

    def title(self, obj):
        """Title of the feed"""
        return _("Results of the search for '%s'") % obj

    def description(self, obj):
        """Description of the feed"""
        return _("The relationtypes containing the pattern '%s'") % obj


class RelationtypeDiscussions(RelationappFeed):
    """Feed for discussions in an relationtype"""
    title_template = 'feeds/discussion_title.html'
    description_template = 'feeds/discussion_description.html'

    def get_object(self, request, year, month, day, slug):
        """Retrieve the discussions by relationtype's slug"""
        return get_object_or_404(Relationtype.published, slug=slug,
                                 creation_date__year=year,
                                 creation_date__month=month,
                                 creation_date__day=day)

    def items(self, obj):
        """Items are the discussions on the relationtype"""
        return obj.discussions[:FEEDS_MAX_ITEMS]

    def item_pubdate(self, item):
        """Publication date of a discussion"""
        return item.submit_date

    def item_link(self, item):
        """URL of the discussion"""
        return item.get_absolute_url()

    def link(self, obj):
        """URL of the relationtype"""
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
        return _('The latest discussions for the relationtype %s') % obj.title


class RelationtypeComments(RelationtypeDiscussions):
    """Feed for comments in an relationtype"""
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    def items(self, obj):
        """Items are the comments on the relationtype"""
        return obj.comments[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the comment"""
        return item.get_absolute_url('#comment_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Comments on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest comments for the relationtype %s') % obj.title

    def item_enclosure_url(self, item):
        """Returns a gravatar image for enclosure"""
        return get_gravatar(item.userinfo['email'])

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class RelationtypePingbacks(RelationtypeDiscussions):
    """Feed for pingbacks in an relationtype"""
    title_template = 'feeds/pingback_title.html'
    description_template = 'feeds/pingback_description.html'

    def items(self, obj):
        """Items are the pingbacks on the relationtype"""
        return obj.pingbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the pingback"""
        return item.get_absolute_url('#pingback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Pingbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest pingbacks for the relationtype %s') % obj.title


class RelationtypeTrackbacks(RelationtypeDiscussions):
    """Feed for trackbacks in an relationtype"""
    title_template = 'feeds/trackback_title.html'
    description_template = 'feeds/trackback_description.html'

    def items(self, obj):
        """Items are the trackbacks on the relationtype"""
        return obj.trackbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the trackback"""
        return item.get_absolute_url('#trackback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Trackbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest trackbacks for the relationtype %s') % obj.title
