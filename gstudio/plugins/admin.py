"""Admin of Gstudio CMS Plugins"""
from django.contrib import admin
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from cms.plugin_rendering import render_placeholder
from cms.admin.placeholderadmin import PlaceholderAdmin

from gstudio.models import Objecttype
from gstudio.admin.objecttype import ObjecttypeAdmin
from gstudio.settings import OBJECTTYPE_BASE_MODEL


class ObjecttypePlaceholderAdmin(PlaceholderAdmin, ObjecttypeAdmin):
    """ObjecttypePlaceholder Admin"""
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
                 (_('Publication'), {'fields': ('sites', 'metatypes',
                                                'tags', 'slug')}))

    def save_model(self, request, objecttype, form, change):
        """Fill the content field with the interpretation
        of the placeholder"""
        context = RequestContext(request)
        objecttype.content = render_placeholder(objecttype.content_placeholder, context)
        super(ObjecttypePlaceholderAdmin, self).save_model(
            request, objecttype, form, change)


if OBJECTTYPE_BASE_MODEL == 'gstudio.plugins.placeholder.ObjecttypePlaceholder':
    admin.site.unregister(Objecttype)
    admin.site.register(Objecttype, ObjecttypePlaceholderAdmin)
