"""Admin of Relationapp"""
from django.contrib import admin
from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.admin.relationtype import RelationtypeAdmin
from relationapp.admin.relation import RelationAdmin


admin.site.register(Relationtype, RelationtypeAdmin)
admin.site.register(Relation, RelationAdmin)

# for reversion support in the  relationapp admin interface


