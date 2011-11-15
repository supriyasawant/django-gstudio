"""Feed to Objectapp command module"""
import sys
from datetime import datetime
from optparse import make_option

from django.utils.html import strip_tags
from django.db.utils import IntegrityError
from django.utils.encoding import smart_str
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.text import truncate_words
from django.template.defaultfilters import slugify
from django.core.management.base import CommandError
from django.core.management.base import LabelCommand

from objectapp import __version__
from objectapp.models import GBObject
from objectapp.models import Objecttype
from objectapp.managers import PUBLISHED
from objectapp.signals import disconnect_objectapp_signals


class Command(LabelCommand):
    """Command object for importing a RSS or Atom
    feed into Objectapp."""
    help = 'Import a RSS or Atom feed into Objectapp.'
    label = 'feed url'
    args = 'url'

    option_list = LabelCommand.option_list + (
        make_option('--noautoexcerpt', action='store_false',
                    dest='auto_excerpt', default=True,
                    help='Do NOT generate an excerpt if not present.'),
        make_option('--author', dest='author', default='',
                    help='All imported gbobjects belong to specified author'),
        make_option('--objecttype-is-tag', action='store_true',
                    dest='objecttype-tag', default=False,
                    help='Store objecttypes as tags'),
        )
    SITE = Site.objects.get_current()

    def __init__(self):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO
        disconnect_objectapp_signals()

    def write_out(self, message, verbosity_level=1):
        """Convenient method for outputing"""
        if self.verbosity and self.verbosity >= verbosity_level:
            sys.stdout.write(smart_str(message))
            sys.stdout.flush()

    def handle_label(self, url, **options):
        try:
            import feedparser
        except ImportError:
            raise CommandError('You need to install the feedparser ' \
                               'module to run this command.')

        self.verbosity = int(options.get('verbosity', 1))
        self.auto_excerpt = options.get('auto_excerpt', True)
        self.default_author = options.get('author')
        self.objecttype_tag = options.get('objecttype-tag', False)
        if self.default_author:
            try:
                self.default_author = User.objects.get(
                    username=self.default_author)
            except User.DoesNotExist:
                raise CommandError('Invalid username for default author')

        self.write_out(self.style.TITLE(
            'Starting importation of %s to Objectapp %s:\n' % (url, __version__)))

        feed = feedparser.parse(url)
        self.import_gbobjects(feed.gbobjects)

    def import_gbobjects(self, feed_gbobjects):
        """Import gbobjects"""
        for feed_gbobject in feed_gbobjects:
            self.write_out('> %s... ' % feed_gbobject.title)
            creation_date = datetime(*feed_gbobject.date_parsed[:6])
            slug = slugify(feed_gbobject.title)[:255]

            if GBObject.objects.filter(creation_date__year=creation_date.year,
                                    creation_date__month=creation_date.month,
                                    creation_date__day=creation_date.day,
                                    slug=slug):
                self.write_out(self.style.NOTICE(
                    'SKIPPED (already imported)\n'))
                continue

            objecttypes = self.import_objecttypes(feed_gbobject)
            gbobject_dict = {'title': feed_gbobject.title[:255],
                          'content': feed_gbobject.description,
                          'excerpt': feed_gbobject.get('summary'),
                          'status': PUBLISHED,
                          'creation_date': creation_date,
                          'start_publication': creation_date,
                          'last_update': datetime.now(),
                          'slug': slug}

            if not gbobject_dict['excerpt'] and self.auto_excerpt:
                gbobject_dict['excerpt'] = truncate_words(
                    strip_tags(feed_gbobject.description), 50)
            if self.objecttype_tag:
                gbobject_dict['tags'] = self.import_tags(objecttypes)

            gbobject = GBObject(**gbobject_dict)
            gbobject.save()
            gbobject.objecttypes.add(*objecttypes)
            gbobject.sites.add(self.SITE)

            if self.default_author:
                gbobject.authors.add(self.default_author)
            elif feed_gbobject.get('author_detail'):
                try:
                    user = User.objects.create_user(
                        slugify(feed_gbobject.author_detail.get('name')),
                        feed_gbobject.author_detail.get('email', ''))
                except IntegrityError:
                    user = User.objects.get(
                        username=slugify(feed_gbobject.author_detail.get('name')))
                gbobject.authors.add(user)

            self.write_out(self.style.ITEM('OK\n'))

    def import_objecttypes(self, feed_gbobject):
        objecttypes = []
        for cat in feed_gbobject.get('tags', ''):
            objecttype, created = Objecttype.objects.get_or_create(
                slug=slugify(cat.term), defaults={'title': cat.term})
            objecttypes.append(objecttype)
        return objecttypes

    def import_tags(self, objecttypes):
        tags = []
        for cat in objecttypes:
            if len(cat.title.split()) > 1:
                tags.append('"%s"' % slugify(cat.title).replace('-', ' '))
            else:
                tags.append(slugify(cat.title).replace('-', ' '))
        return ', '.join(tags)
