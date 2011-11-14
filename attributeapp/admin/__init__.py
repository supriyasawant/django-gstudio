"""Admin of Attributeapp"""
from django.contrib import admin
from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.admin.attributetype import AttributetypeAdmin
from attributeapp.admin.attribute import AttributeAdmin


admin.site.register(Attributetype, AttributetypeAdmin)
admin.site.register(Attribute, AttributeAdmin)

# for reversion support in the  attributeapp admin interface


