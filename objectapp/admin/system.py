"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from objectapp.admin.forms import SystemAdminForm
import reversion

class SystemAdmin(reversion.VersionAdmin):
        form = SystemAdminForm
	prepopulated_fields = {'slug': ('title', )}
	fieldsets = ((_('Content'), {'fields': ('title', 'content','tags', 
                                            'image', 'status')}),
                 (_('System specific'), {'fields': ('systemtypes', 'edgeset','nodeset','systemset')}),
 		   

                 (_('Options'), {'fields': ('featured', 'excerpt', 'template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Discussion'), {'fields': ('comment_enabled',
                                               'pingback_enabled'),
				    'classes': ('collapse', 'collapse-closed')}),
                 (_('Publication'), {'fields': ('sites', 'slug'),
				     'classes': ('collapse', 'collapse-closed')}))             
        def __init__(self, model, admin_site):
            self.form.admin_site = admin_site
            super(SystemAdmin, self).__init__(model, admin_site)

        def get_tree_path(self, System):
            """Return the Objecttype's tree path in HTML"""
            try:
                return '<a href="%s" target="blank">/%s/</a>' % \
                   (System.get_absolute_url(), System.tree_path)
            except NoReverseMatch:
                return '/%s/' % Systemtype.tree_path
            get_tree_path.allow_tags = True
            get_tree_path.short_description = _('tree path')



