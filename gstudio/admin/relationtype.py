"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from gstudio.admin.forms import RelationtypeAdminForm
import reversion



class RelationtypeAdmin(reversion.VersionAdmin):
    form = RelationtypeAdminForm
    prepopulated_fields = {'slug': ('title', )}
    fieldsets = ((
                 (_('Neighbourhood Definiton'), {'fields': (
                                                           'title',
                                                           'inverse', 
                                                           'altnames',
                                                           'parent',
                                                           'slug',

                                                           'subjecttypeLeft',
                                                           'applicablenodetypes1',
                                                           'cardinalityLeft',
                                                           'subjecttypeRight',
                                                           'applicablenodetypes2',
                                                           'cardinalityRight',
                                                           'isSymmetrical',
                                                           'isReflexive',
                                                           'isTransitive') 
                                                }),
                 (_('Content'), {'fields': ('content', 'image',), 
                                 'classes': ('collapse', 'collapse-closed')}),

 		   
                 (_('Dependency'), {'fields': ('priornode', 'posteriornode',), 
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Options'), {'fields': ('featured', 'excerpt', 'template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),

                                 
                 (_('Publication'), {'fields': ('tags', 
                                                'sites')}))
                 )
    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(RelationtypeAdmin, self).__init__(model, admin_site)

    def get_tree_path(self, System):
            """Return the Objecttype's tree path in HTML"""
            try:
                return '<a href="%s" target="blank">/%s/</a>' % \
                   (Relationtype.get_absolute_url(), RelationtypeAdmin.tree_path)
            except NoReverseMatch:
                return '/%s/' % RelationtypeAdmin.tree_path
            get_tree_path.allow_tags = True
            get_tree_path.short_description = _('tree path')



