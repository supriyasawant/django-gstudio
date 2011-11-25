"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from objectapp.admin.forms import ProcessAdminForm
import reversion

class ProcessAdmin(reversion.VersionAdmin):

    pass

