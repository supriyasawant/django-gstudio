"""Plugins for CMS"""
import itertools

from django.conf import settings
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from attributeapp.models import Attributetype
from attributeapp.models import Author
from attributeapp.managers import tags_published
from attributeapp.plugins.models import RandomAttributetypesPlugin
from attributeapp.plugins.models import LatestAttributetypesPlugin
from attributeapp.plugins.models import SelectedAttributetypesPlugin


class CMSLatestAttributetypesPlugin(CMSPluginBase):
    """Django-cms plugin for the latest attributetypes filtered"""
    module = _('attributetypes')
    model = LatestAttributetypesPlugin
    name = _('Latest attributetypes')
    render_template = 'attributeapp/cms/attributetype_list.html'
    filter_horizontal = ['attributes', 'authors', 'tags']
    fieldsets = (
        (None, {
            'fields': (
                'number_of_attributetypes',
                'template_to_render'
            )
        }),
        (_('Sorting'), {
            'fields': (
                'attributes',
                'authors',
                'tags'
            ),
            'classes': (
                'collapse',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'subattributes',
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
        return super(CMSLatestAttributetypesPlugin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        attributetypes = Attributetype.published.all()

        if instance.attributes.count():
            cats = instance.attributes.all()

            if instance.subattributes:
                cats = itertools.chain(cats, *[c.get_descendants()
                                               for c in cats])

            attributetypes = attributetypes.filter(attributes__in=cats)
        if instance.authors.count():
            attributetypes = attributetypes.filter(authors__in=instance.authors.all())
        if instance.tags.count():
            attributetypes = TaggedItem.objects.get_union_by_model(
                attributetypes, instance.tags.all())

        attributetypes = attributetypes.distinct()[:instance.number_of_attributetypes]
        context.update({'attributetypes': attributetypes,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'attributeapp/img/plugin.png'


class CMSSelectedAttributetypesPlugin(CMSPluginBase):
    """Django-cms plugin for a selection of attributetypes"""
    module = _('attributetypes')
    model = SelectedAttributetypesPlugin
    name = _('Selected attributetypes')
    render_template = 'attributeapp/cms/attributetype_list.html'
    fields = ('attributetypes', 'template_to_render')
    filter_horizontal = ['attributetypes']
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update({'attributetypes': instance.attributetypes.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'attributeapp/img/plugin.png'


class CMSRandomAttributetypesPlugin(CMSPluginBase):
    """Django-cms plugin for random attributetypes"""
    module = _('attributetypes')
    model = RandomAttributetypesPlugin
    name = _('Random object types')
    render_template = 'attributeapp/cms/random_attributetypes.html'
    fields = ('number_of_attributetypes', 'template_to_render')
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update(
            {'number_of_attributetypes': instance.number_of_attributetypes,
             'template_to_render': str(instance.template_to_render) or
             'attributeapp/tags/random_attributetypes.html'})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'attributeapp/img/plugin.png'

plugin_pool.register_plugin(CMSLatestAttributetypesPlugin)
plugin_pool.register_plugin(CMSSelectedAttributetypesPlugin)
plugin_pool.register_plugin(CMSRandomAttributetypesPlugin)
