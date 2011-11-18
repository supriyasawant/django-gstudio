"""Admin of Gstudio"""
from django.contrib import admin
from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.models import Relation
from gstudio.models import Relationtype
from gstudio.models import Attribute
from gstudio.models import Attributetype


from gstudio.admin.objecttype import ObjecttypeAdmin
from gstudio.admin.metatype import MetatypeAdmin
from gstudio.admin.relationtype import RelationtypeAdmin
from gstudio.admin.relation import RelationAdmin
from gstudio.admin.attribute import AttributeAdmin
from gstudio.admin.attributetype import AttributetypeAdmin


admin.site.register(Objecttype, ObjecttypeAdmin)

admin.site.register(Metatype, MetatypeAdmin)

admin.site.register(Relationtype, RelationtypeAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Attributetype, AttributetypeAdmin)


