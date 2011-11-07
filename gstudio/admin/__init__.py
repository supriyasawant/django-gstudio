"""Admin of Gstudio"""
from django.contrib import admin

from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.admin.objecttype import ObjecttypeAdmin
from gstudio.admin.metatype import MetatypeAdmin


admin.site.register(Objecttype, ObjecttypeAdmin)
admin.site.register(Metatype, MetatypeAdmin)
