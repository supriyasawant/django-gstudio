"""AttributeAdmin for Attributeapp"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from attributeapp.admin.forms import AttributeAdminForm
import reversion

class AttributeAdmin(reversion.VersionAdmin):
    """Admin for Attribute model"""
    form = AttributeAdminForm
    fields = ('title', 'parent', 'description', 'slug')
    list_display = ('title', 'slug', 'get_tree_path', 'description')
    prepopulated_fields = {'slug': ('title', )}
    search_fields = ('title', 'description')
    list_filter = ('parent',)

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(AttributeAdmin, self).__init__(model, admin_site)

    def get_tree_path(self, attribute):
        """Return the attribute's tree path in HTML"""
        try:
            return '<a href="%s" target="blank">/%s/</a>' % \
                   (attribute.get_absolute_url(), attribute.tree_path)
        except NoReverseMatch:
            return '/%s/' % attribute.tree_path
    get_tree_path.allow_tags = True
    get_tree_path.short_description = _('tree path')
