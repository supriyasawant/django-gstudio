"""Admin of Relationapp CMS Plugins"""
from django.contrib import admin
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from cms.plugin_rendering import render_placeholder
from cms.admin.placeholderadmin import PlaceholderAdmin

from relationapp.models import Relationtype
from relationapp.admin.relationtype import RelationtypeAdmin
from relationapp.settings import RELATIONTYPE_BASE_MODEL


class RelationtypePlaceholderAdmin(PlaceholderAdmin, RelationtypeAdmin):
    """RelationtypePlaceholder Admin"""
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
                 (_('Publication'), {'fields': ('sites', 'relations',
                                                'tags', 'slug')}))

    def save_model(self, request, relationtype, form, change):
        """Fill the content field with the interpretation
        of the placeholder"""
        context = RequestContext(request)
        relationtype.content = render_placeholder(relationtype.content_placeholder, context)
        super(RelationtypePlaceholderAdmin, self).save_model(
            request, relationtype, form, change)


if RELATIONTYPE_BASE_MODEL == 'relationapp.plugins.placeholder.RelationtypePlaceholder':
    admin.site.unregister(Relationtype)
    admin.site.register(Relationtype, RelationtypePlaceholderAdmin)
