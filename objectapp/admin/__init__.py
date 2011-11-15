"""Admin of Objectapp"""
from django.contrib import admin
from objectapp.models import GBObject
from objectapp.models import Objecttype
from objectapp.admin.gbobject import GBObjectAdmin
from objectapp.admin.objecttype import ObjecttypeAdmin


admin.site.register(GBObject, GBObjectAdmin)


# for reversion support in the  objectapp admin interface


