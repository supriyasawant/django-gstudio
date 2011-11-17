"""Admin of Objectapp CMS Plugins"""
from django.contrib import admin
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from cms.plugin_rendering import render_placeholder
from cms.admin.placeholderadmin import PlaceholderAdmin

from objectapp.models import Gbobject
from objectapp.admin.gbobject import GbobjectAdmin
from objectapp.settings import GBOBJECT_BASE_MODEL


class GbobjectPlaceholderAdmin(PlaceholderAdmin, GbobjectAdmin):
    """GbobjectPlaceholder Admin"""
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
                 (_('Publication'), {'fields': ('sites', 'objecttypes',
                                                'tags', 'slug')}))

    def save_model(self, request, gbobject, form, change):
        """Fill the content field with the interpretation
        of the placeholder"""
        context = RequestContext(request)
        gbobject.content = render_placeholder(gbobject.content_placeholder, context)
        super(GbobjectPlaceholderAdmin, self).save_model(
            request, gbobject, form, change)


if GBOBJECT_BASE_MODEL == 'objectapp.plugins.placeholder.GbobjectPlaceholder':
    admin.site.unregister(Gbobject)
    admin.site.register(Gbobject, GbobjectPlaceholderAdmin)
