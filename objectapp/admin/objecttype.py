"""ObjecttypeAdmin for Objectapp"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from objectapp.admin.forms import ObjecttypeAdminForm
import reversion

class ObjecttypeAdmin(reversion.VersionAdmin):
    """Admin for Objecttype model"""
    form = ObjecttypeAdminForm
    fields = ('title','altnames', 'parent', 'description', 'slug')
    list_display = ('title', 'slug', 'get_tree_path', 'description')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description')
    list_filter = ('parent',)

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(ObjecttypeAdmin, self).__init__(model, admin_site)

    def get_tree_path(self, objecttype):
        """Return the objecttype's tree path in HTML"""
        try:
            return '<a href="%s" target="blank">/%s/</a>' % \
                   (Objecttype.get_absolute_url(), Objecttype.tree_path)
        except NoReverseMatch:
            return '/%s/' % Objecttype.tree_path
    get_tree_path.allow_tags = True
    get_tree_path.short_description = _('tree path')
