"""Models of Gstudio CMS Plugins"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _

from tagging.models import Tag
from cms.models import CMSPlugin
from menus.menu_pool import menu_pool

from gstudio.models import Nodetype
from gstudio.models import Metatype
from gstudio.plugins.settings import PLUGINS_TEMPLATES

TEMPLATES = [('gstudio/cms/nodetype_list.html', _('Nodetype list (default)')),
             ('gstudio/cms/nodetype_detail.html', _('Nodetype detailed'))] + \
             PLUGINS_TEMPLATES


class LatestNodetypesPlugin(CMSPlugin):
    """CMS Plugin for displaying latest nodetypes"""

    metatypes = models.ManyToManyField(
        Metatype, verbose_name=_('metatypes'),
        blank=True, null=True)
    submetatypes = models.BooleanField(
        default=True, verbose_name=_('include submetatypes'))
    authors = models.ManyToManyField(
        User, verbose_name=_('authors'), blank=True, null=True)
    tags = models.ManyToManyField(
        Tag, verbose_name=_('tags'), blank=True, null=True)

    number_of_nodetypes = models.IntegerField(
        _('number of nodetypes'), default=5)
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
        self.metatypes = old_instance.metatypes.all()

    def __unicode__(self):
        return _('%s nodetypes') % self.number_of_nodetypes


class SelectedNodetypesPlugin(CMSPlugin):
    """CMS Plugin for displaying custom nodetypes"""

    nodetypes = models.ManyToManyField(
        Nodetype, verbose_name=_('nodetypes'))
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
        self.nodetypes = old_instance.nodetypes.all()

    def __unicode__(self):
        return _('%s nodetypes') % self.nodetypes.count()


class RandomNodetypesPlugin(CMSPlugin):
    """CMS Plugin for displaying random nodetypes"""

    number_of_nodetypes = models.IntegerField(
        _('number of nodetypes'), default=5)
    template_to_render = models.CharField(
        _('template'), blank=True,
        max_length=250, choices=TEMPLATES,
        help_text=_('Template used to display the plugin'))

    def __unicode__(self):
        return _('%s nodetypes') % self.number_of_nodetypes


def invalidate_menu_cache(sender, **kwargs):
    """Signal receiver to invalidate the menu_pool
    cache when an nodetype is posted"""
    menu_pool.clear()

post_save.connect(
    invalidate_menu_cache, sender=Nodetype,
    dispatch_uid='gstudio.nodetype.postsave.invalidate_menu_cache')
post_delete.connect(
    invalidate_menu_cache, sender=Nodetype,
    dispatch_uid='gstudio.nodetype.postdelete.invalidate_menu_cache')
