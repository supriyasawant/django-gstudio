"""Admin of Attributeapp CMS Plugins"""
from django.contrib import admin
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from cms.plugin_rendering import render_placeholder
from cms.admin.placeholderadmin import PlaceholderAdmin

from attributeapp.models import Attributetype
from attributeapp.admin.attributetype import AttributetypeAdmin
from attributeapp.settings import ATTRIBUTETYPE_BASE_MODEL


class AttributetypePlaceholderAdmin(PlaceholderAdmin, AttributetypeAdmin):
    """AttributetypePlaceholder Admin"""
    fieldsets = ((None, {'fields': ('title', 'image', 'status')}),
                 (_('Content'), {'fields': ('content_placeholder',),
                                 'classes': ('plugin-holder',
                                             'plugin-holder-nopage')}),
                 (_('Options'), {'fields': ('featured', 'excerpt', 'template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Discussion'), {'fields': ('comment_enabled',
                                               'pingback_enabled')}),
                 (_('Publication'), {'fields': ('sites', 'attributes',
                                                'tags', 'slug')}))

    def save_model(self, request, attributetype, form, change):
        """Fill the content field with the interpretation
        of the placeholder"""
        context = RequestContext(request)
        attributetype.content = render_placeholder(attributetype.content_placeholder, context)
        super(AttributetypePlaceholderAdmin, self).save_model(
            request, attributetype, form, change)


if ATTRIBUTETYPE_BASE_MODEL == 'attributeapp.plugins.placeholder.AttributetypePlaceholder':
    admin.site.unregister(Attributetype)
    admin.site.register(Attributetype, AttributetypePlaceholderAdmin)
