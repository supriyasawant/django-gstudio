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

from djangoratings.fields import RatingField
from tagging.fields import TagField
from gstudio.settings import UPLOAD_TO
from gstudio.settings import MARKUP_LANGUAGE
from gstudio.settings import NODETYPE_TEMPLATES
from gstudio.settings import NODETYPE_BASE_MODEL
from gstudio.settings import MARKDOWN_EXTENSIONS
from gstudio.settings import AUTO_CLOSE_COMMENTS_AFTER
from gstudio.managers import nodetypes_published
from gstudio.managers import NodetypePublishedManager
from gstudio.managers import AuthorPublishedManager
from gstudio.managers import DRAFT, HIDDEN, PUBLISHED
from gstudio.moderator import NodetypeCommentModerator
from gstudio.url_shortener import get_url_shortener
from gstudio.signals import ping_directories_handler
from gstudio.signals import ping_external_urls_handler
import reversion
from reversion.models import Version
from django.core import serializers

NODETYPE_CHOICES = (
    ('ED', 'Edges'),
    ('ND', 'Nodes'),
    ('NT', 'Node types'),
    ('ET', 'Edge types'),
    ('OT', 'Object types'),
    ('RT', 'Relation types'),
    ('MT', 'Metatypes'),
    ('AT', 'Attribute types'),
    ('RN', 'Relations'),
    ('AS', 'Attributes'),
    ('ST', 'System type'),
    ('SY', 'System'),
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


STATUS_CHOICES = ((DRAFT, _('draft')),
                  (HIDDEN, _('hidden')),
                  (PUBLISHED, _('published')))

class Author(User):
    """Proxy Model around User"""
    
    objects = models.Manager()
    published = AuthorPublishedManager()

    def nodetypes_published(self):
        """Return only the nodetypes published"""
        return nodetypes_published(self.nodetypes)

    @models.permalink
    def get_absolute_url(self):
        """Return author's URL"""
        return ('gstudio_author_detail', (self.username,))

    class Meta:
        """Author's Meta"""
        proxy = True

class NID(models.Model):
    """the set of all nodes.  provides node ID (NID) to all nodes in
    the network, including edges.  Edges are also first class citizens
    in the gnowledge base. """

    title = models.CharField(_('title'), help_text=_('give a name to the node'), max_length=255)

    def get_serialized_dict(self):
        """
        return the fields in a serialized form of the current object using the __dict__ function.
        """
        return self.__dict__

    def get_serialized_data(self):
        """
        return the fields in a serialized form of the current object.
        get object id, go to version model, return serialized_data for the given id
        """
        from reversion.models import Version
        version = Version.objects.get(id=self.id)
        return version.serialized_data

    def __unicode__(self):
        return self.title


    class Meta:
        """NID's Meta"""



class Node(NID):
    """
    Super class 
    """

    altnames = TagField(_('alternate names'), help_text=_('alternate names if any'), blank=True, null=True)
    plural = models.CharField(_('plural name'), help_text=_('plural form of the node name if any'), max_length=255, blank=True, null=True)
    rating = RatingField(range=5, can_change_vote = True, help_text=_('your rating'), blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        abstract=False

class Edge(NID):


    def __unicode__(self):
        return self.title

    class Meta:
        abstract=False


class Metatype(Node):
    """
    Metatype object for Nodetype
    """

    slug = models.SlugField(help_text=_('used for publication'), unique=True, max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    parent = models.ForeignKey('self', null=True, blank=True, verbose_name=_('parent metatype'), related_name='children')


    def nodetypes_published(self):
        """
        Return only the published nodetypes 
        """
        return nodetypes_published(self.nodetypes)

    @property
    def get_nbh(self):
        """  
        Returns the neighbourhood of the metatype
        """
        nbh = {}
        nbh['title'] = self.title
        nbh['altnames'] = self.altnames 
        nbh['plural'] = self.plural
        if self.parent:
            nbh['typeof'] = self.parent
        # generate ids and names of children/members
        nbh['contains_subtypes'] = self.children.get_query_set()
        nbh['contains_members'] = self.nodetypes.all()
        nbh['left_role_of'] = Relationtype.objects.filter(subjecttypeLeft=self.id)
        nbh['right_role_of'] = Relationtype.objects.filter(subjecttypeRight=self.id)
        nbh['attributetypes'] = Attributetype.objects.filter(subjecttype=self.id)
        
        return nbh

                  
    @property
    def tree_path(self):
        """Return metatype's tree path, by its ancestors"""
        if self.parent:
            return '%s/%s' % (self.parent.tree_path, self.slug)
        return self.slug

    def __unicode__(self):
        return self.title

    @property
    def composed_sentence(self):
        "composes the relation as a sentence in triple format."
        if self.parent:
            return '%s is a kind of %s' % (self.title, self.parent.tree_path)
        return '%s is a root node'  % (self.slug)
    

    @models.permalink
    def get_absolute_url(self):
        """Return metatype's URL"""
        return ('gstudio_metatype_detail', (self.tree_path,))


    class Meta:
        """Metatype's Meta"""
        ordering = ['title']
        verbose_name = _('metatype')
        verbose_name_plural = _('metatypes')





class Nodetype(Node):
    """
    Model design for publishing nodetypes.  Other nodetypes inherit this class.
    """



    STATUS_CHOICES = ((DRAFT, _('draft')),
                      (HIDDEN, _('hidden')),
                      (PUBLISHED, _('published')))

    content = models.TextField(_('content'), null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               verbose_name=_('is a kind of'),
                               related_name='subtypes')
    priornodes = models.ManyToManyField('self', null=True, blank=True,
                               verbose_name=_('its meaning depends on '),
                               related_name='posteriors')
    posteriornodes = models.ManyToManyField('self', null=True, blank=True,
                               verbose_name=_('required for the meaning of '),
                               related_name='priornodes')

    image = models.ImageField(_('image'), upload_to=UPLOAD_TO,
                              blank=True, help_text=_('used for illustration'))

    excerpt = models.TextField(_('excerpt'), blank=True,
                                help_text=_('optional element'))

    tags = TagField(_('tags'))
    metatypes = models.ManyToManyField(Metatype, verbose_name=_('member of metatypes'),
                                        related_name='nodetypes',
                                        blank=True, null=True)

    slug = models.SlugField(help_text=_('used for publication'),
                            unique_for_date='creation_date',
                            max_length=255)

    authors = models.ManyToManyField(User, verbose_name=_('authors'),
                                     related_name='nodetypes',
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
                                   related_name='nodetypes')

    login_required = models.BooleanField(
        _('login required'), default=False,
        help_text=_('only authenticated users can view the nodetype'))
    password = models.CharField(
        _('password'), max_length=50, blank=True,
        help_text=_('protect the nodetype with a password'))

    template = models.CharField(
        _('template'), max_length=250,
        default='gstudio/nodetype_detail.html',
        choices=[('gstudio/nodetype_detail.html', _('Default template'))] + \
        NODETYPE_TEMPLATES,
        help_text=_('template used to display the nodetype'))

    objects = models.Manager()
    published = NodetypePublishedManager()

    @property
    def tree_path(self):
        """Return nodetype's tree path, by its ancestors"""
        if self.parent:
            return '%s/%s' % (self.parent.tree_path, self.slug)
        return self.slug

    @property
    def tree_path_sentence(self):
        """ Return the parent of the nodetype in a triple form """
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
    def previous_nodetype(self):
        """Return the previous nodetype"""
        nodetypes = Nodetype.published.filter(
            creation_date__lt=self.creation_date)[:1]
        if nodetypes:
            return nodetypes[0]

    @property
    def next_nodetype(self):
        """Return the next nodetype"""
        nodetypes = Nodetype.published.filter(
            creation_date__gt=self.creation_date).order_by('creation_date')[:1]
        if nodetypes:
            return nodetypes[0]

    @property
    def word_count(self):
        """Count the words of a nodetype"""
        return len(strip_tags(self.html_content).split())

    @property
    def is_actual(self):
        """Check if a nodetype is within publication period"""
        now = datetime.now()
        return now >= self.start_publication and now < self.end_publication

    @property
    def is_visible(self):
        """Check if a nodetype is visible on site"""
        return self.is_actual and self.status == PUBLISHED

    @property
    def related_published(self):
        """Return only related nodetypes published"""
        return nodetypes_published(self.related)

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
        """Return the nodetype's short url"""
        return get_url_shortener()(self)

    def __unicode__(self):
        return self.title

    @property
    def memberof_sentence(self):
        """Return the metatype of which the nodetype is a member of"""
        
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
        "retuns the parent nodetype."
        if self.parent:
            return '%s' % (self.parent.tree_path)
        return None 

    @models.permalink
    def get_absolute_url(self):
        """Return nodetype's URL"""
        return ('gstudio_nodetype_detail', (), {
            'year': self.creation_date.strftime('%Y'),
            'month': self.creation_date.strftime('%m'),
            'day': self.creation_date.strftime('%d'),
            'slug': self.slug})

    def get_serialized_data(self):
        """
        return the fields in a serialized form of the current object.
        get object id, go to version model, return serialized_data for the given id
        """
        from reversion.models import Version
        version = Version.objects.get(id=self.node_ptr_id)
        return version.serialized_data

    class Meta:
        """Nodetype's Meta"""
        ordering = ['-creation_date']
        verbose_name = _('node type')
        verbose_name_plural = _('node types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


class Objecttype(Nodetype):
    '''
    Object class
    '''

    def __unicode__(self):
        return self.title

    @property
    def get_attributetypes(self):        
        return self.subjecttype_GbnodeType.all()

    @property
    def get_relationtypes(self):
        
        left_relset = self.subjecttypeLeft_gbnodetype.all()  
        right_relset = self.subjecttypeRight_gbnodetype.all() 

        reltypes = {}
        reltypes['left_role_of']=left_relset
        reltypes['right_role_of']=right_relset
        return reltypes

    @property
    def get_leftroles(self):
        """
        for which relation types does this object become a domain of any relation type
        """
        reltypes = []
        left_relset = self.subjecttypeLeft_gbnodetype.all()  
        for relationtype in left_relset:
	    reltypes.append(relationtype)
        return reltypes

    @property
    def get_rightroles(self):
        """
        for which relation types does this object become a domain of any relation type
        """
        reltypes = []
        right_relset = self.subjecttypeRight_gbnodetype.all()  
        for relationtype in right_relset:
	    reltypes.append(relationtype)
        return reltypes

    @property
    def get_subjecttypes(self):
        """
        for which relation types does this object become a domain of any relation type
        """
        subjecttypes = []
        attrset = self.subjecttype_GbnodeType.all()  
        for subjecttype in attrset:
	    subjecttypes.append(subjecttype)
        return subjecttypes
        

    @property
    def member_of_metatypes(self):
        """
        returns if the objecttype is a member of the membership in a metatype class
        """
        types = []
        if self.metatypes.all():
            for metatype in self.metatypes.all():    
		types.append(metatype.title)
        return types


    @property
    def get_members(self):
        """
        get members of the object type
        """
        members = []
        if self.gbobjects.all():
            for gbobject in self.gbobjects.all():   
		members.append(gbobject)
        return members    

    @property
    def get_nbh(self):
        """          
        Returns the neighbourhood of the nodetype
        """
        nbh = {}
        nbh['title'] = self.title
        nbh['altnames'] = self.altnames
        nbh['plural'] = self.plural        
        nbh['member_of_metatype'] = self.metatypes.all()
        # get all the ATs for the objecttype
        nbh.update(self.get_attributetypes) 
        # get all the RTs for the objecttype        
        nbh.update(self.get_relationtypes) 

        nbh['type_of'] = self.parent

        nbh['contains_subtypes'] = Nodetype.objects.filter(parent=self.id)
        # get all the objects inheriting this OT 
        nbh['contains_members'] = self.gbobjects.all()

        nbh['priornodes'] = self.priornodes.all()             

        nbh['posteriornodes'] = self.posteriornodes.all() 

	nbh['authors'] = self.authors.all()

	return nbh




    class Meta:
        """
        object type's meta class
        """
        verbose_name = _('object type')
        verbose_name_plural = _('object types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )




class Edgetype(Nodetype):

    def __unicode__(self):
        return self.title

    class Meta:
        abstract=False


class Relationtype(Edgetype):
    '''
    Binary Relationtypes are defined in this table.
    '''
    inverse = models.CharField(_('inverse name'), help_text=_('when subjecttypes are interchanged, what should be the name of the relation type? This is mandatory field. If the relation is symmetric, same name will do.'), max_length=255,db_index=True ) 
    subjecttypeLeft = models.ForeignKey(NID,related_name="subjecttypeLeft_gbnodetype", verbose_name='left role')  
    applicablenodetypes1 = models.CharField(max_length=2,choices=NODETYPE_CHOICES,default='OT', verbose_name='Node types for left role')
    cardinalityLeft = models.IntegerField(null=True, blank=True, verbose_name='cardinality for the left role')
    subjecttypeRight = models.ForeignKey(NID,related_name="subjecttypeRight_gbnodetype", verbose_name='right role')  
    applicablenodetypes2 = models.CharField(max_length=2,choices=NODETYPE_CHOICES,default='OT', verbose_name='Node types for right role')
    cardinalityRight = models.IntegerField(null=True, blank=True, verbose_name='cardinality for the right role')
    isSymmetrical = models.NullBooleanField(verbose_name='Is symmetrical?')
    isReflexive = models.NullBooleanField(verbose_name='Is reflexive?')
    isTransitive = models.NullBooleanField(verbose_name='Is transitive?')


    def get_serialized_data(self):
        """
        return the fields in a serialized form of the current object.
        get object id, go to version model, return serialized_data for the given id
        """
        from reversion.models import Version
        version = Version.objects.get(id=self.node_ptr_id)
        return version.serialized_data


    def __unicode__(self):
        return self.title

    class Meta:
        """
        relation type's meta class
        """
        verbose_name = _('relation type')
        verbose_name_plural = _('relation types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


class Attributetype(Nodetype):
    '''
    To define attributes of objects. First three fields are mandatory.
    The rest of the fields may be required depending on what type of
    field is selected for datatype. 
    '''
    subjecttype = models.ForeignKey(NID, related_name="subjecttype_GbnodeType", verbose_name='subject type name')  
    applicablenodetypes = models.CharField(max_length=2,choices=NODETYPE_CHOICES,default='OT', verbose_name='applicable nodetypes') 
    dataType = models.CharField(max_length=2, choices=FIELD_TYPE_CHOICES,default='01', verbose_name='data type of value') 
 
    verbose_name = models.CharField(max_length=500, null=True, blank=True, verbose_name='verbosename', help_text='verbose name')
    null = models.NullBooleanField(verbose_name='Null', help_text='can the value be null?')
    blank = models.NullBooleanField(verbose_name='Blank', help_text='can the form be left blank?')
    help_text = models.CharField(max_length=500, null=True, blank=True, verbose_name='Help text', help_text='help text for the field')
    max_digits = models.IntegerField(max_length=5, null=True, blank=True, verbose_name='Max digit', help_text='If you have selected Decimal Field for datatype, you have to specify the number of digits.')
    decimal_places = models.IntegerField(max_length=2, null=True, blank=True, verbose_name='Decimal places', help_text='If you have selected Decimal Field for datatype, you have to specify the decimal places.')
    auto_now = models.NullBooleanField(verbose_name='Auto now',  null=True, blank=True, help_text='Use this if DateTime & Time Field was chosen above for datatype') 
    auto_now_add = models.NullBooleanField(verbose_name='Auto now add',  null=True, blank=True, help_text='Use this if DateTime & Time Field was chosen above for datatype')
    upload_to = models.CharField(max_length=500,verbose_name='Upload to', null=True, blank=True, help_text='Required for FileField and ImageField')
    path=models.CharField(max_length=500,verbose_name='Path', null=True, blank=True, help_text='Required for FilePathField')
    verify_exists=models.NullBooleanField(verbose_name='Verify exits', null=True, blank=True, help_text='Required for AttributeURLField')
    min_length=models.IntegerField(max_length=10,null=True, blank=True, verbose_name='min length', help_text='minimum length')
    required=models.NullBooleanField(verbose_name='required', null=True, blank=True, help_text='Use this for setting mandatory and optional fields')
    label=models.CharField(max_length=500, null=True,blank=True,verbose_name='label',help_text='specify the "human-friendly" label')
    unique=models.NullBooleanField(verbose_name='unique', null=True, blank=True, help_text='If True, this field must be unique throughout the table')
    validators=models.ManyToManyField('self', verbose_name='validators',blank=True, null=True,help_text='A list of validators to run for this field')
    default=models.CharField(max_length=500, null=True, blank=True, verbose_name='default', help_text='The default value for the field')
    editable=models.NullBooleanField(verbose_name='required', null=True, blank=True, help_text='If False, the field will not be editable')
    

    def simpleform(self):
        """ create the form elements """
        simpleform = {}
        simpleform['projectName'] = self.subjecttype
        simpleform['ID'] = self.subjecttype
        simpleform['formName'] = self.title
        simpleform['formRef'] = self.title
        return simpleform

    def simpleform_xml(self):
        """
        this function will move to the managaers module with functions
        like gstudio2epicollect and epicollect2gstudio. this is a
        simple example to suggest a usecase to create dynamic forms.
        """

        dictionary = self.simpleform()
        return '<xform>  <model>  <submission id="learning-epicollect" projectName="learning-epicollect" allowDownloadEdits="false" versionNumber="2.1"/>  <uploadToServer>http://test.mlst.net/epicollectplus/school2/upload</uploadToServer>  <downloadFromServer>http://test.mlst.net/epicollectplus/school2/download</downloadFromServer>  </model> <form num="1" name=" %s  " key=" %s " main="true"> ' % (dictionary['projectName'], dictionary['projectName'])  

    def inputform_xml(self):

        """
        this function will move to the managaers module with functions
        like gstudio2epicollect and epicollect2gstudio. this is a
        simple example to suggest a usecase to create dynamic forms.
        """

        return '<input ref="%s" title="true">  <label>what is the %s? </label>  </input>' % (self.title, self.title) 



    def __unicode__(self):
        return self.title

    class Meta:
        """
        attribute type's meta class
        """
        verbose_name = _('attribute type')
        verbose_name_plural = _('attribute types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


    
class Relation(Edge):
    '''
    other defined relations. subject1 and subject2 can be any of the
    nodetypes except relations for now.
    '''

    subject1Scope = models.CharField(max_length=50, verbose_name='subject scope or qualification', null=True, blank=True)
    subject1 = models.ForeignKey(NID, related_name="subject1_gbnode", verbose_name='subject name') 
    relationTypeScope = models.CharField(max_length=50, verbose_name='relation scope or qualification', null=True, blank=True)
    relationtype = models.ForeignKey(Relationtype, verbose_name='relation name')
    objectScope = models.CharField(max_length=50, verbose_name='object scope or qualification', null=True, blank=True)
    subject2 = models.ForeignKey(NID, related_name="subject2_gbnode", verbose_name='object name') 


    class Meta:
        unique_together = (('subject1Scope', 'subject1', 'relationTypeScope', 'relationtype', 'objectScope', 'subject2'),)
        verbose_name = _('relation')
        verbose_name_plural = _('relations')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


    def __unicode__(self):
        return self.composed_sentence

    @property
    def composed_sentence(self):
        "composes the relation as a sentence in a triple format."
        return '%s %s %s %s %s %s' % (self.subject1Scope, self.subject1, self.relationTypeScope, self.relationtype, self.objectScope, self.subject2)

    @property
    def inversed_sentence(self):
        "composes the inverse relation as a sentence in a triple format."
        return '%s %s %s %s %s' % (self.objectScope, self.subject2, self.relationtype.inverse, self.subject1Scope, self.subject1 )

    @property
    def key_value(self):
        return dict({str(self.relationtype):str(self.subject2)})

    @property
    def inverse_key_value(self):
        return dict({str(self.relationtype.inverse):str(self.subject1)})


    @property
    def relation_sentence(self):
        """Return the relations of the objecttypes"""
        
        if self.relationtype:
           # for relation in self.relationtype():
                return '%s %s %s' % (self.subject1,self.relationtype,self.subject2 )


class Attribute(Edge):
    '''
    Attribute value store for default datatype varchar. Subject can be any of the
    nodetypes. 
    '''

    subjectScope = models.CharField(max_length=50, verbose_name='subject scope or qualification', null=True, blank=True)
    subject = models.ForeignKey(NID, related_name="subject_gbnode", verbose_name='subject name') 
    attributeTypeScope = models.CharField(max_length=50, verbose_name='property scope or qualification', null=True, blank=True)
    attributeType = models.ForeignKey(Attributetype, verbose_name='property name')
    valueScope = models.CharField(max_length=50, verbose_name='value scope or qualification', null=True, blank=True)
    svalue  = models.CharField(max_length=100, verbose_name='serialized value') 

    
    class Meta:
        unique_together = (('subjectScope', 'subject', 'attributeTypeScope', 'attributeType', 'valueScope', 'svalue'),)
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


    def __unicode__(self):
        return self.composed_attribution

    @property
    def edge_node_dict(self):
        '''
        composes the attribution as a name:value pair sentence without the subject.
        '''
        return dict({str(self.attributeTypeScope) + str(self.attributeType): str(self.valueScope)+ str(self.svalue)})

    @property
    def composed_sentence(self):
        '''
        composes the attribution as a sentence in a triple format.
        '''
        return '%s %s has %s %s %s %s' % (self.subjectScope, self.subject, self.attributeTypeScope, self.attributeType, self.valueScope, self.svalue)

    @property
    def composed_attribution(self):
        '''
        composes a name to the attribute
        '''
        return 'the %s of %s is %s' % (self.attributeType, self.subject, self.svalue)


class AttributeCharField(Attribute):    

    value  = models.CharField(max_length=100, verbose_name='string') 

    def __unicode__(self):
        return self.title

class AttributeTextField(Attribute):
    
    value  = models.TextField(verbose_name='text') 

    def __unicode__(self):
        return self.title
    
class AttributeIntegerField(Attribute):
     value = models.IntegerField(max_length=100, verbose_name='Integer') 

     def __unicode__(self):
         return self.title

class AttributeCommaSeparatedIntegerField(Attribute):
    
    value  = models.CommaSeparatedIntegerField(max_length=100, verbose_name='integers separated by comma') 

    def __unicode__(self):
        return self.title

class AttributeBigIntegerField(Attribute):
    
    value  = models.BigIntegerField(max_length=100, verbose_name='big integer') 

    def __unicode__(self):
        return self.title

class AttributePositiveIntegerField(Attribute):
    
    value  = models.PositiveIntegerField(max_length=100, verbose_name='positive integer') 

    def __unicode__(self):
        return self.title

class AttributeDecimalField(Attribute):
    
    value  = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='decimal') 

    def __unicode__(self):
        return self.title

class AttributeFloatField(Attribute):
    
    value  = models.FloatField(max_length=100, verbose_name='number as float') 

    def __unicode__(self):
        return self.title

class AttributeBooleanField(Attribute):
    
    value  = models.BooleanField(verbose_name='boolean') 

    def __unicode__(self):
        return self.title

class AttributeNullBooleanField(Attribute):
    
    value  = models.NullBooleanField(verbose_name='true false or unknown') 

    def __unicode__(self):
        return self.title

class AttributeDateField(Attribute):
    
    value  = models.DateField(max_length=100, verbose_name='date') 

    def __unicode__(self):
        return self.title

class AttributeDateTimeField(Attribute):
    
    value  = models.DateTimeField(max_length=100, verbose_name='date time') 
    
    def __unicode__(self):
        return self.title
    
class AttributeTimeField(Attribute):
    
    value  = models.TimeField(max_length=100, verbose_name='time') 

    def __unicode__(self):
        return self.title

class AttributeEmailField(Attribute):
    
    value  = models.CharField(max_length=100,verbose_name='value') 

    def __unicode__(self):
        return self.title

class AttributeFileField(Attribute):
    
    value  = models.FileField(upload_to='/media', verbose_name='file') 

    def __unicode__(self):
        return self.title

class AttributeFilePathField(Attribute):
    
    value  = models.FilePathField(verbose_name='path of file') 

    def __unicode__(self):
        return self.title

class AttributeImageField(Attribute):
    
    value  = models.ImageField(upload_to='/media', verbose_name='image') 

    def __unicode__(self):
        return self.title

class AttributeURLField(Attribute):

    value  = models.URLField(max_length=100, verbose_name='url') 

    def __unicode__(self):
        return self.title

class AttributeIPAddressField(Attribute):

    value  = models.IPAddressField(max_length=100, verbose_name='ip address') 

    def __unicode__(self):
        return self.title


class Processtype(Nodetype):    

    """
    A kind of nodetype for defining processes or events or temporal
    objects involving change.  
    """
    attributetype_set = models.ManyToManyField(Attributetype, null=True, blank=True,
                               verbose_name=_('attribute set involved in the process'),
                               related_name='processtype_attributetypeset')
    relationtype_set = models.ManyToManyField(Relationtype, null=True, blank=True,
                               verbose_name=_('relation set involved in the process'),
                               related_name='processtype_relationtypeset')


    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('process type')
        verbose_name_plural = _('process types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )




class Systemtype(Nodetype):    

    """
    class to organize Systems
    """


    nodetype_set = models.ManyToManyField(Nodetype, related_name="nodetypeset_systemtype", verbose_name='Possible edges in the system',    
                                           blank=True, null=False) 
    relationtype_set = models.ManyToManyField(Relationtype, related_name="relationtypeset_systemtype", verbose_name='Possible nodetypes in the system',    
                                             blank=True, null=False) 
    attributetype_set = models.ManyToManyField(Attributetype, related_name="attributetypeset_systemtype", verbose_name='systems to be nested in the system',
                                              blank=True, null=False)
    metatype_set = models.ManyToManyField(Metatype, related_name="metatypeset_systemtype", verbose_name='Possible edges in the system',    
                                         blank=True, null=False) 
    processtype_set = models.ManyToManyField(Processtype, related_name="processtypeset_systemtype", verbose_name='Possible edges in the system',    
                                            blank=True, null=False) 


    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('system type')
        verbose_name_plural = _('system types')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )
    

class AttributeSpecification(Node):
    """
    specifying an attribute by a subject
    """
    attributetype = models.ForeignKey(Attributetype, verbose_name='property name')
    subjects = models.ManyToManyField(NID, related_name="subjects_attrspec", verbose_name='subjects')


    @property
    def composed_subject(self):
        '''
        composes a name to the attribute
        '''
        return 'the %s of %s' % (self.attributetype, self.subject)


    def __unicode__(self):
        return self.composed_subject


    class Meta:
        verbose_name = _('attribute specification')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


class RelationSpecification(Node):
    """
    specifying a relation with a subject 
    """
    relationtype = models.ForeignKey(Relationtype, verbose_name='relation name')
    subjects = models.ManyToManyField(NID, related_name="subjects_relspec", verbose_name='subjects')


    @property
    def composed_subject(self):
        '''
        composing an expression with relation name and subject
        '''
        return 'the %s of %s' % (self.relationtype, self.subject)

    def __unicode__(self):
        return self.composed_subject


    class Meta:
        verbose_name = _('relation as subject')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


class NodeSpecification(Node):
    """
    A node specified (described) by its relations or attributes or both.  
    """
    subject = models.ForeignKey(Node, related_name="subject_node", verbose_name='subject name')
    relations = models.ManyToManyField(Relation, related_name="relations_nodespec", verbose_name='relations used to specify the domain')
    attributes = models.ManyToManyField(Attribute, related_name="attributes_nodespec", verbose_name='attributes used to specify the domain')
    @property
    def composed_subject(self):
        '''
        composing an expression subject and relations
        '''
        return 'the %s with %s, %s' % (self.subject, self.relations, self.attributes)

    def __unicode__(self):
        return self.composed_subject


    class Meta:
        verbose_name = _('relation as subject')
        permissions = (('can_view_all', 'Can view all'),
                       ('can_change_author', 'Can change author'), )


class Union(Node):
    """
    union of two classes
    """
    nodetypes = models.ManyToManyField(Nodetype, related_name = 'nodetypes_union', verbose_name='node types for union')
        
    def __unicode__(self):
        return self.title

class Complement(Node):
    """
    complement of a  class
    """
    nodetypes = models.ManyToManyField(Nodetype, related_name = 'nodetypes_complement', verbose_name='complementary nodes')
        
    def __unicode__(self):
        return self.title

class Intersection(Node):
    """
    Intersection of classes
    """
    nodetypes = models.ManyToManyField(Nodetype, related_name = 'nodetypes_intersection', verbose_name='intersection of classes')
        
    def __unicode__(self):
        return self.title
    

reversion.register(NID)
reversion.register(Node)
reversion.register(Objecttype)
reversion.register(Edgetype)
reversion.register(Edge)

if not reversion.is_registered(Systemtype):
    reversion.register(Systemtype)

if not reversion.is_registered(Processtype):
    reversion.register(Processtype, follow=["attributetype_set", "relationtype_set"])

if not reversion.is_registered(Nodetype): 
    reversion.register(Nodetype, follow=["parent", "metatypes"])

if not reversion.is_registered(Metatype):
    reversion.register(Metatype, follow=["parent"])

if not reversion.is_registered(Nodetype):
    reversion.register(Nodetype, follow=["priornodes", "posteriornodes"])

if not reversion.is_registered(Relationtype): 
    reversion.register(Relationtype, follow=["subjecttypeLeft", "subjecttypeRight"])

if not reversion.is_registered(Attributetype): 
    reversion.register(Attributetype, follow=["subjecttype"])

if not reversion.is_registered(Attribute): 
    reversion.register(Attribute, follow=["subject", "attributeType"])

if not reversion.is_registered(Relation): 
    reversion.register(Relation, follow=["subject1", "subject2", "relationtype"])

moderator.register(Nodetype, NodetypeCommentModerator)
mptt.register(Metatype, order_insertion_by=['title'])
mptt.register(Nodetype, order_insertion_by=['title'])
mptt.register(Objecttype, order_insertion_by=['title'])
mptt.register(Relationtype, order_insertion_by=['title'])
mptt.register(Attributetype, order_insertion_by=['title'])
mptt.register(Systemtype, order_insertion_by=['title'])
mptt.register(Processtype, order_insertion_by=['title'])
post_save.connect(ping_directories_handler, sender=Nodetype,
                  dispatch_uid='gstudio.nodetype.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Nodetype,
                  dispatch_uid='gstudio.nodetype.post_save.ping_external_urls')



