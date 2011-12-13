"""Models of Objectapp"""
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


from djangoratings.fields import RatingField
from tagging.fields import TagField
from gstudio.models import Nodetype
from gstudio.models import Objecttype
from gstudio.models import Node
from gstudio.models import Edge
from gstudio.models import Systemtype
from gstudio.models import Processtype
from gstudio.models import Attribute
from gstudio.models import Relation

import reversion
from objectapp.settings import UPLOAD_TO
from objectapp.settings import MARKUP_LANGUAGE
from objectapp.settings import GBOBJECT_TEMPLATES
from objectapp.settings import GBOBJECT_BASE_MODEL
from objectapp.settings import MARKDOWN_EXTENSIONS
from objectapp.settings import AUTO_CLOSE_COMMENTS_AFTER
from objectapp.managers import gbobjects_published
from objectapp.managers import GbobjectPublishedManager
from objectapp.managers import AuthorPublishedManager
from objectapp.managers import DRAFT, HIDDEN, PUBLISHED
from objectapp.moderator import GbobjectCommentModerator
from objectapp.url_shortener import get_url_shortener
from objectapp.signals import ping_directories_handler
from objectapp.signals import ping_external_urls_handler


class Author(User):
    """Proxy Model around User"""

    objects = models.Manager()
    published = AuthorPublishedManager()

    def gbobjects_published(self):
        """Return only the gbobjects published"""
        return gbobjects_published(self.gbobjects)

    @models.permalink
    def get_absolute_url(self):
        """Return author's URL"""
        return ('objectapp_author_detail', (self.username,))

    class Meta:
        """Author's Meta"""
        proxy = True


class Gbobject(Node):
    """
    Member nodes of object types. This is actually to be named the
    Object class, since 'Object' is a reserved name in Python, we
    prefix this with 'Gb', to suggest that it is an object of the gnowledge
    base.  System and Process classes also inherit this class.
    """


    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    content = models.TextField(_('content'), null=True, blank=True)
    image = models.ImageField(_('image'), upload_to=UPLOAD_TO,
                              blank=True, help_text=_('used for illustration'))

    excerpt = models.TextField(_('excerpt'), blank=True,
                                help_text=_('optional element'))

    priornodes = models.ManyToManyField('self', null=True, blank=True,
                               verbose_name=_('depends on'),
                               related_name='posteriors')

    posteriornodes = models.ManyToManyField('self', null=True, blank=True,
                               verbose_name=_('required for'),
                               related_name='priornodes')


    tags = TagField(_('tags'))
    objecttypes = models.ManyToManyField(Nodetype, verbose_name=_('member of'),
                                        related_name='gbobjects',
                                        blank=True, null=True)

    slug = models.SlugField(help_text=_('used for publication'),
                            unique_for_date='creation_date',
                            max_length=255)


    authors = models.ManyToManyField(User, verbose_name=_('authors'),
                                     related_name='gbobjects',
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
                                   related_name='gbobjects')

    login_required = models.BooleanField(
        _('login required'), default=False,
        help_text=_('only authenticated users can view the gbobject'))
    password = models.CharField(
        _('password'), max_length=50, blank=True,
        help_text=_('protect the gbobject with a password'))

    template = models.CharField(
        _('template'), max_length=250,
        default='objectapp/gbobject_detail.html',
        choices=[('objectapp/gbobject_detail.html', _('Default template'))] + \
        GBOBJECT_TEMPLATES,
        help_text=_('template used to display the gbobject'))

    objects = models.Manager()
    published = GbobjectPublishedManager()


    def get_relations(self):
        relation_set = {}
        # ALGO to find the relations and their leftroles and rightroles
        # 1. Get the relations containing a reference to the object. Retrieve where it occurs (left or right)
        # 2. Find out which RT they come from.
        # 3. For each RT, create a dict key and a value as a dict. And add the relation as a new key-value pair (rid:subject).
        # 4. If self is in right value, then add inverse relation as RT and add the relation as a new key-value pair (rid:subject).

        left_relset = Relation.objects.filter(subject1=self.id) 
        right_relset = Relation.objects.filter(subject2=self.id) 
        
        #return left_relset + right_relset

        # RT dictionary to store a single relation
        rel_dict ={}
        rel_dict['leftroles'] = {}
        rel_dict['rightroles'] ={}

               
        for relation in left_relset:
            # check if relation already exists
            if relation.relationtype.title not in rel_dict['leftroles'].keys():
                # create a new list field and add to it
                rel_dict['leftroles'][str(relation.relationtype.title)] = []
            # add 
            rel_dict['leftroles'][str(relation.relationtype.title)].append(relation) 

        for relation in right_relset:
            # check if relation exists
            if relation.relationtype.inverse not in rel_dict['rightroles'].keys():
                # create a new list key field and add to it
                rel_dict['rightroles'][str(relation.relationtype.inverse)] = []
                # add to the existing key
            rel_dict['rightroles'][str(relation.relationtype.inverse)].append(relation)

        relation_set.update(rel_dict['leftroles'])
        relation_set.update(rel_dict['rightroles'])
        
        return relation_set
        

    def get_attributes(self):
        attributes =  {}
        for attribute in self.subject_gbnode.all(): #Attribute.objects.filter(subject=self.id):
            for key,value in attribute.edge_node_dict.iteritems():
                attributes[key]= value
                
        return attributes
            

    @property
    def get_nbh(self):
        """ 
        Returns the neighbourhood of the object
        """
        fields = ['title','altname','pluralform']
        nbh = {}
        nbh['title'] = self.title        
        nbh['altnames'] = self.altnames                
        nbh['plural'] = self.plural
        nbh['content'] = self.content
        #return  all OTs the object is linked to
        nbh['member_of'] = self.objecttypes.all()
        
        # get all the relations of the object    
        nbh.update(self.get_relations())
        nbh.update(self.get_attributes())
        # encapsulate the dictionary with its node name as key
        return nbh


    @property
    def get_rendered_nbh(self):
        """ 
        Returns the neighbourhood of the object
        """
        fields = ['title','altname','pluralform']
        nbh = {}
        nbh['title'] = self.title        
        nbh['altnames'] = self.altnames                
        nbh['plural'] = self.plural
        nbh['content'] = self.content
        #return  all OTs the object is linked to
        member_of_list = []
        for each in self.objecttypes.all():
            member_of_list.append('<a href="%s">%s</a>' % (each.get_absolute_url(), each.title)) 
        nbh['member_of'] = member_of_list

        return nbh



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
    def previous_gbobject(self):
        """Return the previous gbobject"""
        gbobjects = Gbobject.published.filter(
            creation_date__lt=self.creation_date)[:1]
        if gbobjects:
            return gbobjects[0]

    @property
    def next_gbobject(self):
        """Return the next gbobject"""
        gbobjects = Gbobject.published.filter(
            creation_date__gt=self.creation_date).order_by('creation_date')[:1]
        if gbobjects:
            return gbobjects[0]

    @property
    def word_count(self):
        """Count the words of an gbobject"""
        return len(strip_tags(self.html_content).split())

    @property
    def is_actual(self):
        """Check if an gbobject is within publication period"""
        now = datetime.now()
        return now >= self.start_publication and now < self.end_publication

    @property
    def is_visible(self):
        """Check if an gbobject is visible on site"""
        return self.is_actual and self.status == PUBLISHED

    @property
    def related_published(self):
        """Return only related gbobjects published"""
        return gbobjects_published(self.related)

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
        """Return the gbobject's short url"""
        return get_url_shortener()(self)

    def __unicode__(self):
        return self.title

    @property
    def memberof_sentence(self):
        """Return the objecttype of which the gbobject is a member of"""
        
        if self.objecttypes.count:
            for each in self.objecttypes.all():
                return '%s is a member of objecttype %s' % (self.title, each)
        return '%s is not a fully defined name, consider making it a member of a suitable objecttype' % (self.title)


    @models.permalink
    def get_absolute_url(self):
        """Return gbobject's URL"""
        return ('objectapp_gbobject_detail', (), {
            'year': self.creation_date.strftime('%Y'),
            'month': self.creation_date.strftime('%m'),
            'day': self.creation_date.strftime('%d'),
            'slug': self.slug})

    class Meta:
        """Gbobject's Meta"""
        ordering = ['-creation_date']
        verbose_name = _('object')
        verbose_name_plural = _('objects')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )



class Process(Gbobject):    

    """
    A store processes, events or changes described as changes in attributes and relations
    """
    processtypes = models.ManyToManyField(Processtype, verbose_name=_('member of process type'),
                                          related_name='processes',
                                          blank=True, null=True)
    priorstate_attribute_set = models.ManyToManyField(Attribute, null=True, blank=True,
                                                      verbose_name=_('priorstate of attribute set'),
                                                      related_name='priorstate_attribute_set')
    priorstate_relation_set = models.ManyToManyField(Relation, null=True, blank=True,
                                                     verbose_name=_('priorsate of relation set'),
                                                     related_name='priorstate_relation_set')

    poststate_attribute_set = models.ManyToManyField(Attribute, null=True, blank=True,
                                                     verbose_name=_('poststate of attribute set'),
                                                     related_name='proststate_attribute_set')

    poststate_relation_set = models.ManyToManyField(Relation, null=True, blank=True,
                               verbose_name=_('poststate of relation set'),
                               related_name='poststate_relation_set')




    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('process')
        verbose_name_plural = _('processes')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


class System(Gbobject):    

    """
    instance of a Systemtype
    """

    systemtypes = models.ManyToManyField(Systemtype, verbose_name=_('member of systemtype'),
                                        related_name='systemtypes',
                                         blank=True, null=True)

    object_set = models.ManyToManyField(Gbobject, related_name="objectset_system", 
                                       verbose_name='objects in the system',    
                                       blank=True, null=False) 

    relation_set = models.ManyToManyField(Relation, related_name="relationset_system", 
                                         verbose_name='relations in the system',    
                                         blank=True, null=False) 

    attribute_set = models.ManyToManyField(Attribute, related_name="attributeset_system", 
                                          verbose_name='attributes in the system',
                                          blank=True, null=False)

    process_set = models.ManyToManyField(Process, related_name="processset_system", 
                                        verbose_name='processes in the system',    
                                        blank=True, null=False) 

    system_set = models.ManyToManyField('self', related_name="systems_system", 
                                       verbose_name='nested systems',
                                       blank=True, null=False)


    def __unicode__(self):
        return self.title


    
if not reversion.is_registered(Process):
    reversion.register(Process, follow=["priorstate_attribute_set", "priorstate_relation_set", "poststate_attribute_set", "poststate_relation_set", "priornodes", "posteriornodes"])

if not reversion.is_registered(System): 
    reversion.register(System, follow=["systemtypes", "object_set", "relation_set", "attribute_set", "process_set", "system_set", "priornodes", "posteriornodes"])

if not reversion.is_registered(Gbobject):
    reversion.register(Gbobject, follow=["objecttypes", "priornodes", "posteriornodes"])


moderator.register(Gbobject, GbobjectCommentModerator)

post_save.connect(ping_directories_handler, sender=Gbobject,
                  dispatch_uid='objectapp.gbobject.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Gbobject,
                  dispatch_uid='objectapp.gbobject.post_save.ping_external_urls')


