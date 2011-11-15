"""Models of Relationapp CMS Plugins"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from cms.models import CMSPlugin
from menus.menu_pool import menu_pool

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.plugins.settings import PLUGINS_TEMPLATES

TEMPLATES = [('relationapp/cms/relationtype_list.html', _('Relationtype list (default)')),
             ('relationapp/cms/relationtype_detail.html', _('Relationtype detailed'))] + \
             PLUGINS_TEMPLATES


class LatestRelationtypesPlugin(CMSPlugin):
    """CMS Plugin for displaying latest relationtypes"""

    relations = models.ManyToManyField(
        Relation, verbose_name=_('relations'),
        blank=True, null=True)
    subrelations = models.BooleanField(
        default=True, verbose_name=_('include subrelations'))
    authors = models.ManyToManyField(
        User, verbose_name=_('authors'), blank=True, null=True)
    tags = models.ManyToManyField(
        Tag, verbose_name=_('tags'), blank=True, null=True)

    number_of_relationtypes = models.IntegerField(
        _('number of relationtypes'), default=5)
    template_to_render = models.CharField(
        _('template'), blank=True,
        max_length=250, choices=TEMPLATES,
        help_text=_('Template used to display the plugin'))

    @property
    def render_template(self):
        """Override render_template to use
        the template_to_render attribute"""
        return self.template_to_render

    def copy_relations(self, old_instance):
        """Duplicate ManyToMany relations on plugin copy"""
        self.tags = old_instance.tags.all()
        self.authors = old_instance.authors.all()
        self.relations = old_instance.relations.all()

    def __unicode__(self):
        return _('%s relationtypes') % self.number_of_relationtypes


class SelectedRelationtypesPlugin(CMSPlugin):
    """CMS Plugin for displaying custom relationtypes"""

    relationtypes = models.ManyToManyField(
        Relationtype, verbose_name=_('relationtypes'))
    template_to_render = models.CharField(
        _('template'), blank=True,
        max_length=250, choices=TEMPLATES,
        help_text=_('Template used to display the plugin'))

    @property
    def render_template(self):
        """Override render_template to use
        the template_to_render attribute"""
        return self.template_to_render

    def copy_relations(self, old_instance):
        """Duplicate ManyToMany relations on plugin copy"""
        self.relationtypes = old_instance.relationtypes.all()

    def __unicode__(self):
        return _('%s relationtypes') % self.relationtypes.count()


class RandomRelationtypesPlugin(CMSPlugin):
    """CMS Plugin for displaying random relationtypes"""

    number_of_relationtypes = models.IntegerField(
        _('number of relationtypes'), default=5)
    template_to_render = models.CharField(
        _('template'), blank=True,
        max_length=250, choices=TEMPLATES,
        help_text=_('Template used to display the plugin'))

    def __unicode__(self):
        return _('%s relationtypes') % self.number_of_relationtypes


def invalidate_menu_cache(sender, **kwargs):
    """Signal receiver to invalidate the menu_pool
    cache when an relationtype is posted"""
    menu_pool.clear()

post_save.connect(
    invalidate_menu_cache, sender=Relationtype,
    dispatch_uid='relationapp.relationtype.postsave.invalidate_menu_cache')
post_delete.connect(
    invalidate_menu_cache, sender=Relationtype,
    dispatch_uid='relationapp.relationtype.postdelete.invalidate_menu_cache')
