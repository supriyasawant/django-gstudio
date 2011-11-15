"""Feed to Relationapp command module"""
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

from relationapp import __version__
from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.managers import PUBLISHED
from relationapp.signals import disconnect_relationapp_signals


class Command(LabelCommand):
    """Command object for importing a RSS or Atom
    feed into Relationapp."""
    help = 'Import a RSS or Atom feed into Relationapp.'
    label = 'feed url'
    args = 'url'

    option_list = LabelCommand.option_list + (
        make_option('--noautoexcerpt', action='store_false',
                    dest='auto_excerpt', default=True,
                    help='Do NOT generate an excerpt if not present.'),
        make_option('--author', dest='author', default='',
                    help='All imported relationtypes belong to specified author'),
        make_option('--relation-is-tag', action='store_true',
                    dest='relation-tag', default=False,
                    help='Store relations as tags'),
        )
    SITE = Site.objects.get_current()

    def __init__(self):
        """Init the Command and add custom styles"""
        super(Command, self).__init__()
        self.style.TITLE = self.style.SQL_FIELD
        self.style.STEP = self.style.SQL_COLTYPE
        self.style.ITEM = self.style.HTTP_INFO
        disconnect_relationapp_signals()

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
        self.relation_tag = options.get('relation-tag', False)
        if self.default_author:
            try:
                self.default_author = User.objects.get(
                    username=self.default_author)
            except User.DoesNotExist:
                raise CommandError('Invalid username for default author')

        self.write_out(self.style.TITLE(
            'Starting importation of %s to Relationapp %s:\n' % (url, __version__)))

        feed = feedparser.parse(url)
        self.import_relationtypes(feed.relationtypes)

    def import_relationtypes(self, feed_relationtypes):
        """Import relationtypes"""
        for feed_relationtype in feed_relationtypes:
            self.write_out('> %s... ' % feed_relationtype.title)
            creation_date = datetime(*feed_relationtype.date_parsed[:6])
            slug = slugify(feed_relationtype.title)[:255]

            if Relationtype.objects.filter(creation_date__year=creation_date.year,
                                    creation_date__month=creation_date.month,
                                    creation_date__day=creation_date.day,
                                    slug=slug):
                self.write_out(self.style.NOTICE(
                    'SKIPPED (already imported)\n'))
                continue

            relations = self.import_relations(feed_relationtype)
            relationtype_dict = {'title': feed_relationtype.title[:255],
                          'content': feed_relationtype.description,
                          'excerpt': feed_relationtype.get('summary'),
                          'status': PUBLISHED,
                          'creation_date': creation_date,
                          'start_publication': creation_date,
                          'last_update': datetime.now(),
                          'slug': slug}

            if not relationtype_dict['excerpt'] and self.auto_excerpt:
                relationtype_dict['excerpt'] = truncate_words(
                    strip_tags(feed_relationtype.description), 50)
            if self.relation_tag:
                relationtype_dict['tags'] = self.import_tags(relations)

            relationtype = Relationtype(**relationtype_dict)
            relationtype.save()
            relationtype.relations.add(*relations)
            relationtype.sites.add(self.SITE)

            if self.default_author:
                relationtype.authors.add(self.default_author)
            elif feed_relationtype.get('author_detail'):
                try:
                    user = User.objects.create_user(
                        slugify(feed_relationtype.author_detail.get('name')),
                        feed_relationtype.author_detail.get('email', ''))
                except IntegrityError:
                    user = User.objects.get(
                        username=slugify(feed_relationtype.author_detail.get('name')))
                relationtype.authors.add(user)

            self.write_out(self.style.ITEM('OK\n'))

    def import_relations(self, feed_relationtype):
        relations = []
        for cat in feed_relationtype.get('tags', ''):
            relation, created = Relation.objects.get_or_create(
                slug=slugify(cat.term), defaults={'title': cat.term})
            relations.append(relation)
        return relations

    def import_tags(self, relations):
        tags = []
        for cat in relations:
            if len(cat.title.split()) > 1:
                tags.append('"%s"' % slugify(cat.title).replace('-', ' '))
            else:
                tags.append(slugify(cat.title).replace('-', ' '))
        return ', '.join(tags)
