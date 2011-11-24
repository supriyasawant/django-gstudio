"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from gstudio.admin.forms import AttributeAdminForm
import reversion

class AttributeAdmin(reversion.VersionAdmin):
    def save_model(self, request, attribute, form, change):
        attribute.title = attribute.composed_sentence
        attribute.save()



