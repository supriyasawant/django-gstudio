"""Plugins for CMS"""
import itertools

from django.conf import settings
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from gstudio.models import Objecttype
from gstudio.models import Author
from gstudio.managers import tags_published
from gstudio.plugins.models import RandomObjecttypesPlugin
from gstudio.plugins.models import LatestObjecttypesPlugin
from gstudio.plugins.models import SelectedObjecttypesPlugin


class CMSLatestObjecttypesPlugin(CMSPluginBase):
    """Django-cms plugin for the latest objecttypes filtered"""
    module = _('objecttypes')
    model = LatestObjecttypesPlugin
    name = _('Latest objecttypes')
    render_template = 'gstudio/cms/objecttype_list.html'
    filter_horizontal = ['metatypes', 'authors', 'tags']
    fieldsets = (
        (None, {
            'fields': (
                'number_of_objecttypes',
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
        return super(CMSLatestObjecttypesPlugin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        objecttypes = Objecttype.published.all()

        if instance.metatypes.count():
            cats = instance.metatypes.all()

            if instance.submetatypes:
                cats = itertools.chain(cats, *[c.get_descendants()
                                               for c in cats])

            objecttypes = objecttypes.filter(metatypes__in=cats)
        if instance.authors.count():
            objecttypes = objecttypes.filter(authors__in=instance.authors.all())
        if instance.tags.count():
            objecttypes = TaggedItem.objects.get_union_by_model(
                objecttypes, instance.tags.all())

        objecttypes = objecttypes.distinct()[:instance.number_of_objecttypes]
        context.update({'objecttypes': objecttypes,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'gstudio/img/plugin.png'


class CMSSelectedObjecttypesPlugin(CMSPluginBase):
    """Django-cms plugin for a selection of objecttypes"""
    module = _('objecttypes')
    model = SelectedObjecttypesPlugin
    name = _('Selected objecttypes')
    render_template = 'gstudio/cms/objecttype_list.html'
    fields = ('objecttypes', 'template_to_render')
    filter_horizontal = ['objecttypes']
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update({'objecttypes': instance.objecttypes.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'gstudio/img/plugin.png'


class CMSRandomObjecttypesPlugin(CMSPluginBase):
    """Django-cms plugin for random objecttypes"""
    module = _('objecttypes')
    model = RandomObjecttypesPlugin
    name = _('Random objecttypes')
    render_template = 'gstudio/cms/random_objecttypes.html'
    fields = ('number_of_objecttypes', 'template_to_render')
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update(
            {'number_of_objecttypes': instance.number_of_objecttypes,
             'template_to_render': str(instance.template_to_render) or
             'gstudio/tags/random_objecttypes.html'})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'gstudio/img/plugin.png'

plugin_pool.register_plugin(CMSLatestObjecttypesPlugin)
plugin_pool.register_plugin(CMSSelectedObjecttypesPlugin)
plugin_pool.register_plugin(CMSRandomObjecttypesPlugin)
