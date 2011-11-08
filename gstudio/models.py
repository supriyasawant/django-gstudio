"""Models of Gstudio"""
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

from gstudio.settings import UPLOAD_TO
from gstudio.settings import MARKUP_LANGUAGE
from gstudio.settings import OBJECTTYPE_TEMPLATES
from gstudio.settings import OBJECTTYPE_BASE_MODEL
from gstudio.settings import MARKDOWN_EXTENSIONS
from gstudio.settings import AUTO_CLOSE_COMMENTS_AFTER
from gstudio.managers import objecttypes_published
from gstudio.managers import ObjecttypePublishedManager
from gstudio.managers import AuthorPublishedManager
from gstudio.managers import DRAFT, HIDDEN, PUBLISHED
from gstudio.moderator import ObjecttypeCommentModerator
from gstudio.url_shortener import get_url_shortener
from gstudio.signals import ping_directories_handler
from gstudio.signals import ping_external_urls_handler


class Author(User):
    """Proxy Model around User"""

    objects = models.Manager()
    published = AuthorPublishedManager()

    def objecttypes_published(self):
        """Return only the objecttypes published"""
        return objecttypes_published(self.objecttypes)

    @models.permalink
    def get_absolute_url(self):
        """Return author's URL"""
        return ('gstudio_author_detail', (self.username,))

    class Meta:
        """Author's Meta"""
        proxy = True


class Metatype(models.Model):
    """Metatype object for Objecttype"""

    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(help_text=_('used for publication'),
                            unique=True, max_length=255)
    description = models.TextField(_('description'), blank=True)

    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('parent metatype'),
                               related_name='children')

    def objecttypes_published(self):
        """Return only the objecttypes published"""
        return objecttypes_published(self.objecttypes)

    @property
    def tree_path(self):
        """Return metatype's tree path, by his ancestors"""
        if self.parent:
            return '%s/%s' % (self.parent.tree_path, self.slug)
        return self.slug

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        """Return metatype's URL"""
        return ('gstudio_metatype_detail', (self.tree_path,))

    class Meta:
        """Metatype's Meta"""
        ordering = ['title']
        verbose_name = _('metatype')
        verbose_name_plural = _('metatypes')


class Objecttype(models.Model):
    """Model design publishing objecttypes"""
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    title = models.CharField(_('title'), max_length=255)

    image = models.ImageField(_('image'), upload_to=UPLOAD_TO,
                              blank=True, help_text=_('used for illustration'))
    content = models.TextField(_('content'), blank=True), help_text=_('brief description of the node'),
    excerpt = models.TextField(_('excerpt'), blank=True,
                                help_text=_('optional element'))

    tags = TagField(_('tags'))
    metatypes = models.ManyToManyField(Metatype, verbose_name=_('metatypes'),
                                        related_name='objecttypes',
                                        blank=True, null=True)
    related = models.ManyToManyField('self', verbose_name=_('related objecttypes'),
                                     blank=True, null=True)

    slug = models.SlugField(help_text=_('used for publication'),
                            unique_for_date='creation_date',
                            max_length=255)

    authors = models.ManyToManyField(User, verbose_name=_('authors'),
                                     related_name='objecttypes',
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
                                   related_name='objecttypes')

    login_required = models.BooleanField(
        _('login required'), default=False,
        help_text=_('only authenticated users can view the objecttype'))
    password = models.CharField(
        _('password'), max_length=50, blank=True,
        help_text=_('protect the objecttype with a password'))

    template = models.CharField(
        _('template'), max_length=250,
        default='gstudio/objecttype_detail.html',
        choices=[('gstudio/objecttype_detail.html', _('Default template'))] + \
        OBJECTTYPE_TEMPLATES,
        help_text=_('template used to display the objecttype'))

    objects = models.Manager()
    published = ObjecttypePublishedManager()

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
    def previous_objecttype(self):
        """Return the previous objecttype"""
        objecttypes = Objecttype.published.filter(
            creation_date__lt=self.creation_date)[:1]
        if objecttypes:
            return objecttypes[0]

    @property
    def next_objecttype(self):
        """Return the next objecttype"""
        objecttypes = Objecttype.published.filter(
            creation_date__gt=self.creation_date).order_by('creation_date')[:1]
        if objecttypes:
            return objecttypes[0]

    @property
    def word_count(self):
        """Count the words of an objecttype"""
        return len(strip_tags(self.html_content).split())

    @property
    def is_actual(self):
        """Check if an objecttype is within publication period"""
        now = datetime.now()
        return now >= self.start_publication and now < self.end_publication

    @property
    def is_visible(self):
        """Check if an objecttype is visible on site"""
        return self.is_actual and self.status == PUBLISHED

    @property
    def related_published(self):
        """Return only related objecttypes published"""
        return objecttypes_published(self.related)

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
        """Return the objecttype's short url"""
        return get_url_shortener()(self)

    def __unicode__(self):
        return '%s: %s' % (self.title, self.get_status_display())

    @models.permalink
    def get_absolute_url(self):
        """Return objecttype's URL"""
        return ('gstudio_objecttype_detail', (), {
            'year': self.creation_date.strftime('%Y'),
            'month': self.creation_date.strftime('%m'),
            'day': self.creation_date.strftime('%d'),
            'slug': self.slug})


    class Meta:
        """Objecttype's Meta"""
        ordering = ['-creation_date']
        verbose_name = _('object type')
        verbose_name_plural = _('object types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


moderator.register(Objecttype, ObjecttypeCommentModerator)
mptt.register(Metatype, order_insertion_by=['title'])
post_save.connect(ping_directories_handler, sender=Objecttype,
                  dispatch_uid='gstudio.objecttype.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Objecttype,
                  dispatch_uid='gstudio.objecttype.post_save.ping_external_urls')
