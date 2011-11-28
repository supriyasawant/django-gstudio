"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from objectapp.admin.forms import SystemAdminForm
import reversion

class SystemAdmin(reversion.VersionAdmin):
        form = SystemAdminForm
        def __init__(self, model, admin_site):
            self.form.admin_site = admin_site
            super(SystemAdmin, self).__init__(model, admin_site)

        def get_tree_path(self, Objecttype):
            """Return the Objecttype's tree path in HTML"""
            try:
                return '<a href="%s" target="blank">/%s/</a>' % \
                   (Systentype.get_absolute_url(), Objecttype.tree_path)
            except NoReverseMatch:
                return '/%s/' % Systemtype.tree_path
            get_tree_path.allow_tags = True
            get_tree_path.short_description = _('tree path')



