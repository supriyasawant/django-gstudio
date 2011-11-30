"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from gstudio.admin.forms import SystemtypeAdminForm
import reversion

class SystemtypeAdmin(reversion.VersionAdmin):

    form = SystemtypeAdminForm
    prepopulated_fields = {'slug': ('title', )}


    fieldsets = ((_('Neighbourhood'), {'fields': ('title', 'content', 'parent',
                                            'image', 'slug','status')}),
 		   
                 (_('Dependency'), {'fields': ('priornode', 'posteriornode',), 
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Options'), {'fields': ('featured', 'excerpt', 'template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Publication'), {'fields': ('tags', 
                                                'sites')}))
    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(SystemtypeAdmin, self).__init__(model, admin_site)

    def get_tree_path(self, System):
            """Return the Objecttype's tree path in HTML"""
            try:
                return '<a href="%s" target="blank">/%s/</a>' % \
                   (Systemtype.get_absolute_url(), Systemtype.tree_path)
            except NoReverseMatch:
                return '/%s/' % Systemtype.tree_path
            get_tree_path.allow_tags = True
            get_tree_path.short_description = _('tree path')




