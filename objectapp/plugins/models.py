"""Models of Objectapp CMS Plugins"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from cms.models import CMSPlugin
from menus.menu_pool import menu_pool

from objectapp.models import GBObject
from objectapp.models import Objecttype
from objectapp.plugins.settings import PLUGINS_TEMPLATES

TEMPLATES = [('objectapp/cms/gbobject_list.html', _('GBObject list (default)')),
             ('objectapp/cms/gbobject_detail.html', _('GBObject detailed'))] + \
             PLUGINS_TEMPLATES


class LatestGBObjectsPlugin(CMSPlugin):
    """CMS Plugin for displaying latest gbobjects"""

    objecttypes = models.ManyToManyField(
        Objecttype, verbose_name=_('objecttypes'),
        blank=True, null=True)
    subobjecttypes = models.BooleanField(
        default=True, verbose_name=_('include subobjecttypes'))
    authors = models.ManyToManyField(
        User, verbose_name=_('authors'), blank=True, null=True)
    tags = models.ManyToManyField(
        Tag, verbose_name=_('tags'), blank=True, null=True)

    number_of_gbobjects = models.IntegerField(
        _('number of gbobjects'), default=5)
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
        self.objecttypes = old_instance.objecttypes.all()

    def __unicode__(self):
        return _('%s gbobjects') % self.number_of_gbobjects


class SelectedGBObjectsPlugin(CMSPlugin):
    """CMS Plugin for displaying custom gbobjects"""

    gbobjects = models.ManyToManyField(
        GBObject, verbose_name=_('gbobjects'))
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
        self.gbobjects = old_instance.gbobjects.all()

    def __unicode__(self):
        return _('%s gbobjects') % self.gbobjects.count()


class RandomGBObjectsPlugin(CMSPlugin):
    """CMS Plugin for displaying random gbobjects"""

    number_of_gbobjects = models.IntegerField(
        _('number of gbobjects'), default=5)
    template_to_render = models.CharField(
        _('template'), blank=True,
        max_length=250, choices=TEMPLATES,
        help_text=_('Template used to display the plugin'))

    def __unicode__(self):
        return _('%s gbobjects') % self.number_of_gbobjects


def invalidate_menu_cache(sender, **kwargs):
    """Signal receiver to invalidate the menu_pool
    cache when an gbobject is posted"""
    menu_pool.clear()

post_save.connect(
    invalidate_menu_cache, sender=GBObject,
    dispatch_uid='objectapp.gbobject.postsave.invalidate_menu_cache')
post_delete.connect(
    invalidate_menu_cache, sender=GBObject,
    dispatch_uid='objectapp.gbobject.postdelete.invalidate_menu_cache')
