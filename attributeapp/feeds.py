"""Feeds for Attributeapp"""
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

from attributeapp.models import Attributetype
from attributeapp.settings import COPYRIGHT
from attributeapp.settings import PROTOCOL
from attributeapp.settings import FEEDS_FORMAT
from attributeapp.settings import FEEDS_MAX_ITEMS
from attributeapp.managers import attributetypes_published
from attributeapp.views.attributes import get_attribute_or_404
from attributeapp.templatetags.attributeapp_tags import get_gravatar


class AttributeappFeed(Feed):
    """Base Feed for Attributeapp"""
    feed_copyright = COPYRIGHT

    def __init__(self):
        self.site = Site.objects.get_current()
        self.site_url = '%s://%s' % (PROTOCOL, self.site.domain)
        if FEEDS_FORMAT == 'atom':
            self.feed_type = Atom1Feed
            self.subtitle = self.description


class AttributetypeFeed(AttributeappFeed):
    """Base Attributetype Feed"""
    title_template = 'feeds/attributetype_title.html'
    description_template = 'feeds/attributetype_description.html'

    def item_pubdate(self, item):
        """Publication date of an attributetype"""
        return item.creation_date

    def item_attributes(self, item):
        """Attributetype's attributes"""
        return [attribute.title for attribute in item.attributes.all()]

    def item_author_name(self, item):
        """Returns the first author of an attributetype"""
        if item.authors.count():
            self.item_author = item.authors.all()[0]
            return self.item_author.username

    def item_author_email(self, item):
        """Returns the first author's email"""
        return self.item_author.email

    def item_author_link(self, item):
        """Returns the author's URL"""
        try:
            author_url = reverse('attributeapp_author_detail',
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


class LatestAttributetypes(AttributetypeFeed):
    """Feed for the latest attributetypes"""

    def link(self):
        """URL of latest attributetypes"""
        return reverse('attributeapp_attributetype_archive_index')

    def items(self):
        """Items are published attributetypes"""
        return Attributetype.published.all()[:FEEDS_MAX_ITEMS]

    def title(self):
        """Title of the feed"""
        return '%s - %s' % (self.site.name, _('Latest attributetypes'))

    def description(self):
        """Description of the feed"""
        return _('The latest attributetypes for the site %s') % self.site.name


class AttributeAttributetypes(AttributetypeFeed):
    """Feed filtered by a attribute"""

    def get_object(self, request, path):
        """Retrieve the attribute by his path"""
        return get_attribute_or_404(path)

    def items(self, obj):
        """Items are the published attributetypes of the attribute"""
        return obj.attributetypes_published()[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the attribute"""
        return obj.get_absolute_url()

    def title(self, obj):
        """Title of the feed"""
        return _('Attributetypes for the attribute %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest attributetypes for the attribute %s') % obj.title


class AuthorAttributetypes(AttributetypeFeed):
    """Feed filtered by an author"""

    def get_object(self, request, username):
        """Retrieve the author by his username"""
        return get_object_or_404(User, username=username)

    def items(self, obj):
        """Items are the published attributetypes of the author"""
        return attributetypes_published(obj.attributetypes)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the author"""
        return reverse('attributeapp_author_detail', args=[obj.username])

    def title(self, obj):
        """Title of the feed"""
        return _('Attributetypes for author %s') % obj.username

    def description(self, obj):
        """Description of the feed"""
        return _('The latest attributetypes by %s') % obj.username


class TagAttributetypes(AttributetypeFeed):
    """Feed filtered by a tag"""

    def get_object(self, request, slug):
        """Retrieve the tag by his name"""
        return get_object_or_404(Tag, name=slug)

    def items(self, obj):
        """Items are the published attributetypes of the tag"""
        return TaggedItem.objects.get_by_model(
            Attributetype.published.all(), obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the tag"""
        return reverse('attributeapp_tag_detail', args=[obj.name])

    def title(self, obj):
        """Title of the feed"""
        return _('Attributetypes for the tag %s') % obj.name

    def description(self, obj):
        """Description of the feed"""
        return _('The latest attributetypes for the tag %s') % obj.name


class SearchAttributetypes(AttributetypeFeed):
    """Feed filtered by a search pattern"""

    def get_object(self, request):
        """The GET parameter 'pattern' is the object"""
        pattern = request.GET.get('pattern', '')
        if len(pattern) < 3:
            raise ObjectDoesNotExist
        return pattern

    def items(self, obj):
        """Items are the published attributetypes founds"""
        return Attributetype.published.search(obj)[:FEEDS_MAX_ITEMS]

    def link(self, obj):
        """URL of the search request"""
        return '%s?pattern=%s' % (reverse('attributeapp_attributetype_search'), obj)

    def title(self, obj):
        """Title of the feed"""
        return _("Results of the search for '%s'") % obj

    def description(self, obj):
        """Description of the feed"""
        return _("The attributetypes containing the pattern '%s'") % obj


class AttributetypeDiscussions(AttributeappFeed):
    """Feed for discussions in an attributetype"""
    title_template = 'feeds/discussion_title.html'
    description_template = 'feeds/discussion_description.html'

    def get_object(self, request, year, month, day, slug):
        """Retrieve the discussions by attributetype's slug"""
        return get_object_or_404(Attributetype.published, slug=slug,
                                 creation_date__year=year,
                                 creation_date__month=month,
                                 creation_date__day=day)

    def items(self, obj):
        """Items are the discussions on the attributetype"""
        return obj.discussions[:FEEDS_MAX_ITEMS]

    def item_pubdate(self, item):
        """Publication date of a discussion"""
        return item.submit_date

    def item_link(self, item):
        """URL of the discussion"""
        return item.get_absolute_url()

    def link(self, obj):
        """URL of the attributetype"""
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
        return _('The latest discussions for the attributetype %s') % obj.title


class AttributetypeComments(AttributetypeDiscussions):
    """Feed for comments in an attributetype"""
    title_template = 'feeds/comment_title.html'
    description_template = 'feeds/comment_description.html'

    def items(self, obj):
        """Items are the comments on the attributetype"""
        return obj.comments[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the comment"""
        return item.get_absolute_url('#comment_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Comments on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest comments for the attributetype %s') % obj.title

    def item_enclosure_url(self, item):
        """Returns a gravatar image for enclosure"""
        return get_gravatar(item.userinfo['email'])

    def item_enclosure_length(self, item):
        """Hardcoded enclosure length"""
        return '100000'

    def item_enclosure_mime_type(self, item):
        """Hardcoded enclosure mimetype"""
        return 'image/jpeg'


class AttributetypePingbacks(AttributetypeDiscussions):
    """Feed for pingbacks in an attributetype"""
    title_template = 'feeds/pingback_title.html'
    description_template = 'feeds/pingback_description.html'

    def items(self, obj):
        """Items are the pingbacks on the attributetype"""
        return obj.pingbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the pingback"""
        return item.get_absolute_url('#pingback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Pingbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest pingbacks for the attributetype %s') % obj.title


class AttributetypeTrackbacks(AttributetypeDiscussions):
    """Feed for trackbacks in an attributetype"""
    title_template = 'feeds/trackback_title.html'
    description_template = 'feeds/trackback_description.html'

    def items(self, obj):
        """Items are the trackbacks on the attributetype"""
        return obj.trackbacks[:FEEDS_MAX_ITEMS]

    def item_link(self, item):
        """URL of the trackback"""
        return item.get_absolute_url('#trackback_%(id)s')

    def title(self, obj):
        """Title of the feed"""
        return _('Trackbacks on %s') % obj.title

    def description(self, obj):
        """Description of the feed"""
        return _('The latest trackbacks for the attributetype %s') % obj.title
