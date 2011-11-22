"""Super models of Gstudio  """
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
import reversion

NODETYPE_CHOICES = (
    ('OT', 'Objecttypes'),
    ('RT', 'Relationtypes'),
    ('MT', 'Metatypes'),
    ('AT', 'Attributetypes'),
   )

DEPTYPE_CHOICES = (
    ('0', 'Concept-Concept'),
    ('1', 'Activity-Activity'),
    ('2', 'Question-Question'),
    ('3', 'Concept-Activity'),
    ('4', 'Activity-Concept'),
    ('5', 'Question-Concept'),
    ('6', 'Concept-Question'),
    ('7', 'Question-Activity'),
    ('8', 'Activity-Question'),
   )

FIELD_TYPE_CHOICES = (
    ('1', 'CharField'),    
    ('2', 'TextField'),    
    ('3', 'IntegerField'),    
    ('4', 'CommaSeparatedIntegerField'),
    ('5', 'BigIntegerField'),    
    ('6', 'PositiveIntegerField'),    
    ('7', 'DecimalField'),
    ('8', 'FloatField'),
    ('9', 'BooleanField'),
    ('10', 'NullBooleanField'),
    ('11', 'DateField'),
    ('12', 'DateTimeField'),
    ('13', 'TimeField'),    
    ('14', 'EmailField'),
    ('15', 'FileField'),
    ('16', 'FilePathField'),
    ('17', 'ImageField'),
    ('18', 'URLField'),    
    ('19', 'IPAddressField'),
    )

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


class Node(models.Model):

    title = models.CharField(_('title'), max_length=255)

    def __unicode__(self):
        return self.title

    class Meta:
        abstract=False


    
class Nodetype(Node):

    def __unicode__(self):
        return self.title

    class Meta:
        abstract=False



class Metatype(Nodetype):
    """Metatype object for Objecttype"""


    slug = models.SlugField(help_text=_('used for publication'), unique=True, max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)

    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('parent metatype'),
                               related_name='children')

    def objecttypes_published(self):
        """Return only the objecttypes published"""
        return objecttypes_published(self.objecttypes)



    @property
    def get_nbh(self):
        """ Returns the neighbourhood of the metatype """
        nbh = {}
        nbh['title'] = self.title        
        
        nbh['parent'] = {}
        if self.parent:
            nbh['parent'] = dict({str(self.parent.id) : str(self.parent.title)})
        #nbh['related'] = self.related.values_list()
        nbh['children'] = []
        
        # generate ids and names of children/members
        for obj in self.children.get_query_set():  
            nbh['children'].append({str(obj.id):str(obj.title)})

        nbh['members'] = []
        for obj in self.objecttypes.all():
            nbh['members'].append({str(obj.id):str(obj.title)})

        return nbh

                  
    @property
    def tree_path(self):
        """Return metatype's tree path, by its ancestors"""
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
        """Return metatype's URL"""
        return ('gstudio_metatype_detail', (self.tree_path,))


    class Meta:
        """Metatype's Meta"""
        ordering = ['title']
        verbose_name = _('metatype')
        verbose_name_plural = _('metatypes')


class Objecttype(Nodetype):
    """Model design publishing objecttypes"""
    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    content = models.TextField(_('content'), blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('has parent objecttype'),
                               related_name='subtypes')
    priornode = models.ManyToManyField('self', null=True, blank=True,
                               verbose_name=_('has prior nodes'),
                               related_name='posteriors')
    posteriornode = models.ManyToManyField('self', null=True, blank=True,
                               verbose_name=_('has posterior nodes'),
                               related_name='priornodes')

    image = models.ImageField(_('image'), upload_to=UPLOAD_TO,
                              blank=True, help_text=_('used for illustration'))

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
    def get_nbh(self):
        """ Returns the neighbourhood of the metatype """
        nbh = {}
        nbh['title'] = self.title        
        #nbh['content'] = self.content
        nbh['parent'] = {}
        if self.parent:
            nbh['parent'] = dict({str(self.parent.id) : str(self.parent.title)})
        #nbh['related'] = self.related.values_list()
        nbh['children'] = []
        
        # generate ids and names of children/members
        for objecttype in self.get_children():
            nbh['children'].append({str(objecttype.id):str(objecttype.title)})

        nbh['subtypeof'] = []
        for objecttype in self.metatypes.all():
            nbh['subtypeof'].append({str(objecttype.id):str(objecttype.title)})

        return nbh



    @property
    def tree_path(self):
        """Return objecttype's tree path, by its ancestors"""
        if self.parent:
            return '%s/%s' % (self.parent.tree_path, self.slug)
        return self.slug

    @property
    def tree_path_sentence(self):
        """ Return the parent of the objecttype in a triple form """
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
        return self.title

    @property
    def memberof_sentence(self):
        """Return the metatype of which the objecttype is a member of"""
        
        if self.metatypes.count:
            for each in self.metatypes.all():
                return '%s is a member of metatype %s' % (self.title, each)
        return '%s is not a fully defined name, consider making it a member of a suitable metatype' % (self.title)

    @property
    def subtypeof_sentence(self):
        "composes the relation as a sentence in triple format."
        if self.parent:
            return '%s is a subtype of %s' % (self.title, self.parent.tree_path)
        return '%s is a root node' % (self.title)
    composed_sentence = property(subtypeof_sentence)

    def subtypeof(self):
        "retuns the parent objecttype."
        if self.parent:
            return '%s' % (self.parent.tree_path)
        return None 



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




class Relationtype(Nodetype):
    '''
    Binary Relationtypes are defined in this table.
    '''

    subjecttypeLeft = models.ForeignKey(Nodetype,related_name="subjecttypeLeft_gbnodetype", verbose_name='left role')  
    applicablenodetypes1 = models.CharField(max_length=2,choices=NODETYPE_CHOICES,default='OT', verbose_name='Node types for left role')
    cardinalityLeft = models.IntegerField(null=True, blank=True, verbose_name='cardinality for the left role')
    subjecttypeRight = models.ForeignKey(Nodetype,related_name="subjecttypeRight_gbnodetype", verbose_name='right role')  
    applicablenodetypes2 = models.CharField(max_length=2,choices=NODETYPE_CHOICES,default='OT', verbose_name='Node types for right role')
    cardinalityRight = models.IntegerField(null=True, blank=True, verbose_name='cardinality for the right role')
    isSymmetrical = models.NullBooleanField(verbose_name='Is symmetrical?')
    isReflexive = models.NullBooleanField(verbose_name='Is reflexive?')
    isTransitive = models.NullBooleanField(verbose_name='Is transitive?')
   

    def __unicode__(self):
        return self.title

class Attributetype(Nodetype):
    '''
    datatype properties
    '''
    subjecttype = models.ForeignKey(Nodetype, related_name="subjecttype_GbnodeType") 
    applicablenodetypes = models.CharField(max_length=2,choices=NODETYPE_CHOICES,default='OT')
    dataType = models.CharField(max_length=2, choices=FIELD_TYPE_CHOICES,default='01')

    def __unicode__(self):
        return self.title

    
class Relation(models.Model):
    '''
    other defined relations. subject1 and subject2 can be any of the
    nodetypes except relations for now.
    '''

    subject1Scope = models.CharField(max_length=50, verbose_name='subject scope', null=True, blank=True)
    subject1 = models.ForeignKey(Node, related_name="subject1_gbnode", verbose_name='subject name') 
    relationTypeScope = models.CharField(max_length=50, verbose_name='relation scope', null=True, blank=True)
    relationtype = models.ForeignKey(Relationtype, verbose_name='relation name')
    objectScope = models.CharField(max_length=50, verbose_name='object scope', null=True, blank=True)
    subject2 = models.ForeignKey(Node, related_name="subject2_gbnode", verbose_name='object name') 
    title = models.CharField(_('title'), max_length=255)

    class Meta:
        unique_together = (('subject1Scope', 'subject1', 'relationTypeScope', 'relationtype', 'objectScope', 'subject2'),)

    def __unicode__(self):
        return self.composed_sentence

    def _get_sentence(self):
        "composes the relation as a sentence in a triple format."
        return '%s %s %s %s %s %s' % (self.subject1Scope, self.subject1, self.relationTypeScope, self.relationtype, self.objectScope, self.subject2)
    composed_sentence = property(_get_sentence)

class Attribute(models.Model):
    '''
    Attribute value store for default datatype varchar. Subject can be any of the
    nodetypes. 
    '''

    subjectScope = models.CharField(max_length=50, verbose_name='subject scope', null=True, blank=True)
    subject = models.ForeignKey(Node, related_name="subject_gbnode", verbose_name='subject name') 
    attributeTypeScope = models.CharField(max_length=50, verbose_name='property scope', null=True, blank=True)
    attributeType = models.ForeignKey(Attributetype, verbose_name='property name')
    valueScope = models.CharField(max_length=50, verbose_name='value scope', null=True, blank=True)
    value  = models.CharField(max_length=100, verbose_name='value') 
    title = models.CharField(_('title'), max_length=255)
    
    class Meta:
        unique_together = (('subjectScope', 'subject', 'attributeTypeScope', 'attributeType', 'valueScope', 'value'),)

    def __unicode__(self):
        return self.composed_sentence

    def _get_sentence(self):
        '''
        composes the attribution as a sentence in a triple format.
        '''
        return '%s %s has %s %s %s %s' % (self.subjectScope, self.subject, self.attributeTypeScope, self.attributeType, self.valueScope, self.value)
    composed_sentence = property(_get_sentence)

reversion.register(Node)
reversion.register(Nodetype)
if not reversion.is_registered(Objecttype): 
    reversion.register(Objecttype, follow=["parent"])
if not reversion.is_registered(Objecttype):
    reversion.register(Objecttype, follow=["metatypes"])

if not reversion.is_registered(Metatype):
    reversion.register(Metatype, follow=["parent"])

if not reversion.is_registered(Objecttype):
    reversion.register(Objecttype, follow=["priornode"])
if not reversion.is_registered(Objecttype):
    reversion.register(Objecttype, follow=["posteriornode"])

if not reversion.is_registered(Relationtype): 
    reversion.register(Relationtype, follow=["subjecttypeLeft"])
if not reversion.is_registered(Relationtype): 
    reversion.register(Relationtype, follow=["subjecttypeRight"])

if not reversion.is_registered(Attributetype): 
    reversion.register(Attributetype, follow=["subjecttype"])


if not reversion.is_registered(Attribute): 
    reversion.register(Attribute, follow=["subject"])
if not reversion.is_registered(Attribute): 
    reversion.register(Attribute, follow=["attributetype"])

if not reversion.is_registered(Relation): 
    reversion.register(Relation, follow=["subject1"])
if not reversion.is_registered(Relation): 
    reversion.register(Relation, follow=["subject2"])
if not reversion.is_registered(Relation): 
    reversion.register(Relation, follow=["relationtype"])


moderator.register(Objecttype, ObjecttypeCommentModerator)
mptt.register(Metatype, order_insertion_by=['title'])
mptt.register(Objecttype, order_insertion_by=['title'])
post_save.connect(ping_directories_handler, sender=Objecttype,
                  dispatch_uid='gstudio.objecttype.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Objecttype,
                  dispatch_uid='gstudio.objecttype.post_save.ping_external_urls')

