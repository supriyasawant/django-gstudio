"""Models of Relationapp"""
import warnings
from datetime import datetime

from django.db import models
from django.db.models import Q
from django.utils.html import strip_tags
from django.utils.html import linebreaks
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models.signals import post_save
from django.utils.importlib import import_module
from django.contrib import comments
from django.contrib.comments.models import CommentFlag
from django.contrib.comments.moderation import moderator
from django.utils.translation import ugettext_lazy as _

from django.contrib.markup.templatetags.markup import markdown
from django.contrib.markup.templatetags.markup import textile
from django.contrib.markup.templatetags.markup import restructuredtext

import mptt
from tagging.fields import TagField

from relationapp.settings import UPLOAD_TO
from relationapp.settings import MARKUP_LANGUAGE
from relationapp.settings import RELATIONTYPE_TEMPLATES
from relationapp.settings import RELATIONTYPE_BASE_MODEL
from relationapp.settings import MARKDOWN_EXTENSIONS
from relationapp.settings import AUTO_CLOSE_COMMENTS_AFTER
from relationapp.managers import relationtypes_published
from relationapp.managers import RelationtypePublishedManager
from relationapp.managers import AuthorPublishedManager
from relationapp.managers import DRAFT, HIDDEN, PUBLISHED
from relationapp.moderator import RelationtypeCommentModerator
from relationapp.url_shortener import get_url_shortener
from relationapp.signals import ping_directories_handler
from relationapp.signals import ping_external_urls_handler
import reversion

class Author(User):
    """Proxy Model around User"""

    objects = models.Manager()
    published = AuthorPublishedManager()

    def relationtypes_published(self):
        """Return only the relationtypes published"""
        return relationtypes_published(self.relationtypes)

    @models.permalink
    def get_absolute_url(self):
        """Return author's URL"""
        return ('relationapp_author_detail', (self.username,))

    class Meta:
        """Author's Meta"""
        proxy = True


class Relation(models.Model):
    """Relation object for Relationtype"""

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(help_text=_('used for publication'),
                            unique=True, max_length=255)
    description = models.TextField(_('description'), blank=True)

    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('parent relation'),
                               related_name='children')

    def relationtypes_published(self):
        """Return only the relationtypes published"""
        return relationtypes_published(self.relationtypes)

            
    @property
    def tree_path(self):
        """Return relation's tree path, by its ancestors"""
        if self.parent:
            return '%s/%s' % (self.parent.tree_path, self.slug)
        return self.slug

    def __unicode__(self):
        return self.title

    def _get_sentence(self):
        "composes the relation as a sentence in triple format."
        if self.parent:
            return '%s is a kind of %s' % (self.title, self.parent.tree_path)
        return '%s is a root node'  % (self.slug)
    composed_sentence = property(_get_sentence)

    @models.permalink
    def get_absolute_url(self):
        """Return relation's URL"""
        return ('relationapp_relation_detail', (self.tree_path,))


    class Meta:
        """Relation's Meta"""
        ordering = ['title']
        verbose_name = _('relation')
        verbose_name_plural = _('relations')


class Relationtype(models.Model):
    """Model design publishing relationtypes"""
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    title = models.CharField(_('title'), max_length=255)
    content = models.TextField(_('content'))
    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('has parent relationtype'),
                               related_name='subtypes')

    image = models.ImageField(_('image'), upload_to=UPLOAD_TO,
                              blank=True, help_text=_('used for illustration'))

    excerpt = models.TextField(_('excerpt'), blank=True,
                                help_text=_('optional element'))

    tags = TagField(_('tags'))
    relations = models.ManyToManyField(Relation, verbose_name=_('relations'),
                                        related_name='relationtypes',
                                        blank=True, null=True)
    related = models.ManyToManyField('self', verbose_name=_('related relationtypes'),
                                     blank=True, null=True)

    slug = models.SlugField(help_text=_('used for publication'),
                            unique_for_date='creation_date',
                            max_length=255)

    authors = models.ManyToManyField(User, verbose_name=_('authors'),
                                     related_name='relationtypes',
                                     blank=True, null=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=PUBLISHED)

    featured = models.BooleanField(_('featured'), default=False)
    comment_enabled = models.BooleanField(_('comment enabled'), default=True)
    pingback_enabled = models.BooleanField(_('linkback enabled'), default=True)

    creation_date = models.DateTimeField(_('creation date'),
                                         default=datetime.now)
    last_update = models.DateTimeField(_('last update'), default=datetime.now)
    start_publication = models.DateTimeField(_('start publication'),
                                             help_text=_('date start publish'),
                                             default=datetime.now)
    end_publication = models.DateTimeField(_('end publication'),
                                           help_text=_('date end publish'),
                                           default=datetime(2042, 3, 15))

    sites = models.ManyToManyField(Site, verbose_name=_('sites publication'),
                                   related_name='relationtypes')

    login_required = models.BooleanField(
        _('login required'), default=False,
        help_text=_('only authenticated users can view the relationtype'))
    password = models.CharField(
        _('password'), max_length=50, blank=True,
        help_text=_('protect the relationtype with a password'))

    template = models.CharField(
        _('template'), max_length=250,
        default='relationapp/relationtype_detail.html',
        choices=[('relationapp/relationtype_detail.html', _('Default template'))] + \
        RELATIONTYPE_TEMPLATES,
        help_text=_('template used to display the relationtype'))

    objects = models.Manager()
    published = RelationtypePublishedManager()

    @property
    def tree_path(self):
        """Return relationtype's tree path, by its ancestors"""
        if self.parent:
            return '%s/%s' % (self.parent.tree_path, self.slug)
        return self.slug

    @property
    def tree_path_sentence(self):
        """ Return the parent of the relationtype in a triple form """
        if self.parent:
            return '%s is a kind of %s' % (self.title, self.parent.tree_path)
        return '%s is a root node' % (self.title)

    @property
    def html_content(self):
        """Return the content correctly formatted"""
        if MARKUP_LANGUAGE == 'markdown':
            return markdown(self.content, MARKDOWN_EXTENSIONS)
        elif MARKUP_LANGUAGE == 'textile':
            return textile(self.content)
        elif MARKUP_LANGUAGE == 'restructuredtext':
            return restructuredtext(self.content)
        elif not '</p>' in self.content:
            return linebreaks(self.content)
        return self.content


    @property
    def previous_relationtype(self):
        """Return the previous relationtype"""
        relationtypes = Relationtype.published.filter(
            creation_date__lt=self.creation_date)[:1]
        if relationtypes:
            return relationtypes[0]

    @property
    def next_relationtype(self):
        """Return the next relationtype"""
        relationtypes = Relationtype.published.filter(
            creation_date__gt=self.creation_date).order_by('creation_date')[:1]
        if relationtypes:
            return relationtypes[0]

    @property
    def word_count(self):
        """Count the words of an relationtype"""
        return len(strip_tags(self.html_content).split())

    @property
    def is_actual(self):
        """Check if an relationtype is within publication period"""
        now = datetime.now()
        return now >= self.start_publication and now < self.end_publication

    @property
    def is_visible(self):
        """Check if an relationtype is visible on site"""
        return self.is_actual and self.status == PUBLISHED

    @property
    def related_published(self):
        """Return only related relationtypes published"""
        return relationtypes_published(self.related)

    @property
    def discussions(self):
        """Return published discussions"""
        return comments.get_model().objects.for_model(
            self).filter(is_public=True)

    @property
    def comments(self):
        """Return published comments"""
        return self.discussions.filter(Q(flags=None) | Q(
            flags__flag=CommentFlag.MODERATOR_APPROVAL))

    @property
    def pingbacks(self):
        """Return published pingbacks"""
        return self.discussions.filter(flags__flag='pingback')

    @property
    def trackbacks(self):
        """Return published trackbacks"""
        return self.discussions.filter(flags__flag='trackback')

    @property
    def comments_are_open(self):
        """Check if comments are open"""
        if AUTO_CLOSE_COMMENTS_AFTER and self.comment_enabled:
            return (datetime.now() - self.start_publication).days < \
                   AUTO_CLOSE_COMMENTS_AFTER
        return self.comment_enabled

    @property
    def short_url(self):
        """Return the relationtype's short url"""
        return get_url_shortener()(self)

    def __unicode__(self):
        return self.title

    @property
    def memberof_sentence(self):
        """Return the relation of which the relationtype is a member of"""
        
        if self.relations.count:
            for each in self.relations.all():
                return '%s is a member of relation %s' % (self.title, each)
        return '%s is not a fully defined name, consider making it a member of a suitable relation' % (self.title)

    @property
    def subtypeof_sentence(self):
        "composes the relation as a sentence in triple format."
        if self.parent:
            return '%s is a subtype of %s' % (self.title, self.parent.tree_path)
        return '%s is a root node' % (self.title)
    composed_sentence = property(subtypeof_sentence)

    def subtypeof(self):
        "retuns the parent relationtype."
        if self.parent:
            return '%s' % (self.parent.tree_path)
        return None 



    @models.permalink
    def get_absolute_url(self):
        """Return relationtype's URL"""
        return ('relationapp_relationtype_detail', (), {
            'year': self.creation_date.strftime('%Y'),
            'month': self.creation_date.strftime('%m'),
            'day': self.creation_date.strftime('%d'),
            'slug': self.slug})

    class Meta:
        """Relationtype's Meta"""
        ordering = ['-creation_date']
        verbose_name = _('relation type')
        verbose_name_plural = _('relation types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )

if not reversion.is_registered(Relationtype): 
    reversion.register(Relationtype, follow=["parent"])
if not reversion.is_registered(Relationtype):
    reversion.register(Relationtype, follow=["relations"])

if not reversion.is_registered(Relation):
    reversion.register(Relation, follow=["parent"])


moderator.register(Relationtype, RelationtypeCommentModerator)
mptt.register(Relation, order_insertion_by=['title'])
mptt.register(Relationtype, order_insertion_by=['title'])
post_save.connect(ping_directories_handler, sender=Relationtype,
                  dispatch_uid='relationapp.relationtype.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Relationtype,
                  dispatch_uid='relationapp.relationtype.post_save.ping_external_urls')

