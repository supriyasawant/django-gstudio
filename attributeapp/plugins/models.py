"""Models of Attributeapp CMS Plugins"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from cms.models import CMSPlugin
from menus.menu_pool import menu_pool

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.plugins.settings import PLUGINS_TEMPLATES

TEMPLATES = [('attributeapp/cms/attributetype_list.html', _('Attributetype list (default)')),
             ('attributeapp/cms/attributetype_detail.html', _('Attributetype detailed'))] + \
             PLUGINS_TEMPLATES


class LatestAttributetypesPlugin(CMSPlugin):
    """CMS Plugin for displaying latest attributetypes"""

    attributes = models.ManyToManyField(
        Attribute, verbose_name=_('attributes'),
        blank=True, null=True)
    subattributes = models.BooleanField(
        default=True, verbose_name=_('include subattributes'))
    authors = models.ManyToManyField(
        User, verbose_name=_('authors'), blank=True, null=True)
    tags = models.ManyToManyField(
        Tag, verbose_name=_('tags'), blank=True, null=True)

    number_of_attributetypes = models.IntegerField(
        _('number of attributetypes'), default=5)
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
        self.attributes = old_instance.attributes.all()

    def __unicode__(self):
        return _('%s attributetypes') % self.number_of_attributetypes


class SelectedAttributetypesPlugin(CMSPlugin):
    """CMS Plugin for displaying custom attributetypes"""

    attributetypes = models.ManyToManyField(
        Attributetype, verbose_name=_('attributetypes'))
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
        self.attributetypes = old_instance.attributetypes.all()

    def __unicode__(self):
        return _('%s attributetypes') % self.attributetypes.count()


class RandomAttributetypesPlugin(CMSPlugin):
    """CMS Plugin for displaying random attributetypes"""

    number_of_attributetypes = models.IntegerField(
        _('number of attributetypes'), default=5)
    template_to_render = models.CharField(
        _('template'), blank=True,
        max_length=250, choices=TEMPLATES,
        help_text=_('Template used to display the plugin'))

    def __unicode__(self):
        return _('%s attributetypes') % self.number_of_attributetypes


def invalidate_menu_cache(sender, **kwargs):
    """Signal receiver to invalidate the menu_pool
    cache when an attributetype is posted"""
    menu_pool.clear()

post_save.connect(
    invalidate_menu_cache, sender=Attributetype,
    dispatch_uid='attributeapp.attributetype.postsave.invalidate_menu_cache')
post_delete.connect(
    invalidate_menu_cache, sender=Attributetype,
    dispatch_uid='attributeapp.attributetype.postdelete.invalidate_menu_cache')
