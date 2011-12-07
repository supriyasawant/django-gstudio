"""Plugins for CMS"""
import itertools

from django.conf import settings
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from gstudio.models import Nodetype
from gstudio.models import Author
from gstudio.managers import tags_published
from gstudio.plugins.models import RandomNodetypesPlugin
from gstudio.plugins.models import LatestNodetypesPlugin
from gstudio.plugins.models import SelectedNodetypesPlugin


class CMSLatestNodetypesPlugin(CMSPluginBase):
    """Django-cms plugin for the latest nodetypes filtered"""
    module = _('nodetypes')
    model = LatestNodetypesPlugin
    name = _('Latest nodetypes')
    render_template = 'gstudio/cms/nodetype_list.html'
    filter_horizontal = ['metatypes', 'authors', 'tags']
    fieldsets = (
        (None, {
            'fields': (
                'number_of_nodetypes',
                'template_to_render'
            )
        }),
        (_('Sorting'), {
            'fields': (
                'metatypes',
                'authors',
                'tags'
            ),
            'classes': (
                'collapse',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'submetatypes',
            ),
        }),
    )

    text_enabled = True

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Filtering manytomany field"""
        if db_field.name == 'authors':
            kwargs['queryset'] = Author.published.all()
        if db_field.name == 'tags':
            kwargs['queryset'] = tags_published()
        return super(CMSLatestNodetypesPlugin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        nodetypes = Nodetype.published.all()

        if instance.metatypes.count():
            cats = instance.metatypes.all()

            if instance.submetatypes:
                cats = itertools.chain(cats, *[c.get_descendants()
                                               for c in cats])

            nodetypes = nodetypes.filter(metatypes__in=cats)
        if instance.authors.count():
            nodetypes = nodetypes.filter(authors__in=instance.authors.all())
        if instance.tags.count():
            nodetypes = TaggedItem.objects.get_union_by_model(
                nodetypes, instance.tags.all())

        nodetypes = nodetypes.distinct()[:instance.number_of_nodetypes]
        context.update({'nodetypes': nodetypes,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'gstudio/img/plugin.png'


class CMSSelectedNodetypesPlugin(CMSPluginBase):
    """Django-cms plugin for a selection of nodetypes"""
    module = _('nodetypes')
    model = SelectedNodetypesPlugin
    name = _('Selected nodetypes')
    render_template = 'gstudio/cms/nodetype_list.html'
    fields = ('nodetypes', 'template_to_render')
    filter_horizontal = ['nodetypes']
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update({'nodetypes': instance.nodetypes.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'gstudio/img/plugin.png'


class CMSRandomNodetypesPlugin(CMSPluginBase):
    """Django-cms plugin for random nodetypes"""
    module = _('nodetypes')
    model = RandomNodetypesPlugin
    name = _('Random node types')
    render_template = 'gstudio/cms/random_nodetypes.html'
    fields = ('number_of_nodetypes', 'template_to_render')
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update(
            {'number_of_nodetypes': instance.number_of_nodetypes,
             'template_to_render': str(instance.template_to_render) or
             'gstudio/tags/random_nodetypes.html'})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'gstudio/img/plugin.png'

plugin_pool.register_plugin(CMSLatestNodetypesPlugin)
plugin_pool.register_plugin(CMSSelectedNodetypesPlugin)
plugin_pool.register_plugin(CMSRandomNodetypesPlugin)
