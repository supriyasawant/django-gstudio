"""Plugins for CMS"""
import itertools

from django.conf import settings
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from objectapp.models import GBObject
from objectapp.models import Author
from objectapp.managers import tags_published
from objectapp.plugins.models import RandomGBObjectsPlugin
from objectapp.plugins.models import LatestGBObjectsPlugin
from objectapp.plugins.models import SelectedGBObjectsPlugin


class CMSLatestGBObjectsPlugin(CMSPluginBase):
    """Django-cms plugin for the latest gbobjects filtered"""
    module = _('gbobjects')
    model = LatestGBObjectsPlugin
    name = _('Latest gbobjects')
    render_template = 'objectapp/cms/gbobject_list.html'
    filter_horizontal = ['objecttypes', 'authors', 'tags']
    fieldsets = (
        (None, {
            'fields': (
                'number_of_gbobjects',
                'template_to_render'
            )
        }),
        (_('Sorting'), {
            'fields': (
                'objecttypes',
                'authors',
                'tags'
            ),
            'classes': (
                'collapse',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'subobjecttypes',
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
        return super(CMSLatestGBObjectsPlugin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        gbobjects = GBObject.published.all()

        if instance.objecttypes.count():
            cats = instance.objecttypes.all()

            if instance.subobjecttypes:
                cats = itertools.chain(cats, *[c.get_descendants()
                                               for c in cats])

            gbobjects = gbobjects.filter(objecttypes__in=cats)
        if instance.authors.count():
            gbobjects = gbobjects.filter(authors__in=instance.authors.all())
        if instance.tags.count():
            gbobjects = TaggedItem.objects.get_union_by_model(
                gbobjects, instance.tags.all())

        gbobjects = gbobjects.distinct()[:instance.number_of_gbobjects]
        context.update({'gbobjects': gbobjects,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'objectapp/img/plugin.png'


class CMSSelectedGBObjectsPlugin(CMSPluginBase):
    """Django-cms plugin for a selection of gbobjects"""
    module = _('gbobjects')
    model = SelectedGBObjectsPlugin
    name = _('Selected gbobjects')
    render_template = 'objectapp/cms/gbobject_list.html'
    fields = ('gbobjects', 'template_to_render')
    filter_horizontal = ['gbobjects']
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update({'gbobjects': instance.gbobjects.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'objectapp/img/plugin.png'


class CMSRandomGBObjectsPlugin(CMSPluginBase):
    """Django-cms plugin for random gbobjects"""
    module = _('gbobjects')
    model = RandomGBObjectsPlugin
    name = _('Random object types')
    render_template = 'objectapp/cms/random_gbobjects.html'
    fields = ('number_of_gbobjects', 'template_to_render')
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update(
            {'number_of_gbobjects': instance.number_of_gbobjects,
             'template_to_render': str(instance.template_to_render) or
             'objectapp/tags/random_gbobjects.html'})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'objectapp/img/plugin.png'

plugin_pool.register_plugin(CMSLatestGBObjectsPlugin)
plugin_pool.register_plugin(CMSSelectedGBObjectsPlugin)
plugin_pool.register_plugin(CMSRandomGBObjectsPlugin)
