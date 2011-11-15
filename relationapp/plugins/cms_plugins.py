"""Plugins for CMS"""
import itertools

from django.conf import settings
from django.utils.translation import ugettext as _

from tagging.models import TaggedItem
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.managers import tags_published
from relationapp.plugins.models import RandomRelationtypesPlugin
from relationapp.plugins.models import LatestRelationtypesPlugin
from relationapp.plugins.models import SelectedRelationtypesPlugin


class CMSLatestRelationtypesPlugin(CMSPluginBase):
    """Django-cms plugin for the latest relationtypes filtered"""
    module = _('relationtypes')
    model = LatestRelationtypesPlugin
    name = _('Latest relationtypes')
    render_template = 'relationapp/cms/relationtype_list.html'
    filter_horizontal = ['relations', 'authors', 'tags']
    fieldsets = (
        (None, {
            'fields': (
                'number_of_relationtypes',
                'template_to_render'
            )
        }),
        (_('Sorting'), {
            'fields': (
                'relations',
                'authors',
                'tags'
            ),
            'classes': (
                'collapse',
            )
        }),
        (_('Advanced'), {
            'fields': (
                'subrelations',
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
        return super(CMSLatestRelationtypesPlugin, self).formfield_for_manytomany(
            db_field, request, **kwargs)

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        relationtypes = Relationtype.published.all()

        if instance.relations.count():
            cats = instance.relations.all()

            if instance.subrelations:
                cats = itertools.chain(cats, *[c.get_descendants()
                                               for c in cats])

            relationtypes = relationtypes.filter(relations__in=cats)
        if instance.authors.count():
            relationtypes = relationtypes.filter(authors__in=instance.authors.all())
        if instance.tags.count():
            relationtypes = TaggedItem.objects.get_union_by_model(
                relationtypes, instance.tags.all())

        relationtypes = relationtypes.distinct()[:instance.number_of_relationtypes]
        context.update({'relationtypes': relationtypes,
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'relationapp/img/plugin.png'


class CMSSelectedRelationtypesPlugin(CMSPluginBase):
    """Django-cms plugin for a selection of relationtypes"""
    module = _('relationtypes')
    model = SelectedRelationtypesPlugin
    name = _('Selected relationtypes')
    render_template = 'relationapp/cms/relationtype_list.html'
    fields = ('relationtypes', 'template_to_render')
    filter_horizontal = ['relationtypes']
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update({'relationtypes': instance.relationtypes.all(),
                        'object': instance,
                        'placeholder': placeholder})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'relationapp/img/plugin.png'


class CMSRandomRelationtypesPlugin(CMSPluginBase):
    """Django-cms plugin for random relationtypes"""
    module = _('relationtypes')
    model = RandomRelationtypesPlugin
    name = _('Random object types')
    render_template = 'relationapp/cms/random_relationtypes.html'
    fields = ('number_of_relationtypes', 'template_to_render')
    text_enabled = True

    def render(self, context, instance, placeholder):
        """Update the context with plugin's data"""
        context.update(
            {'number_of_relationtypes': instance.number_of_relationtypes,
             'template_to_render': str(instance.template_to_render) or
             'relationapp/tags/random_relationtypes.html'})
        return context

    def icon_src(self, instance):
        """Icon source of the plugin"""
        return settings.STATIC_URL + u'relationapp/img/plugin.png'

plugin_pool.register_plugin(CMSLatestRelationtypesPlugin)
plugin_pool.register_plugin(CMSSelectedRelationtypesPlugin)
plugin_pool.register_plugin(CMSRandomRelationtypesPlugin)
