"""Admin of Gstudio"""
from django.contrib import admin

#Models import
from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.models import Relation
from gstudio.models import Relationtype
from gstudio.models import Attribute
from gstudio.models import Attributetype
from gstudio.models import Systemtype
from gstudio.models import Processtype
from gstudio.models import AttributeSpecification
from gstudio.models import RelationSpecification
from gstudio.models import NodeSpecification
from gstudio.models import Union
from gstudio.models import Complement
from gstudio.models import Intersection

#Admin imports

from gstudio.admin.objecttype import ObjecttypeAdmin
from gstudio.admin.metatype import MetatypeAdmin
from gstudio.admin.relationtype import RelationtypeAdmin
from gstudio.admin.relation import RelationAdmin
from gstudio.admin.attribute import AttributeAdmin
from gstudio.admin.attributetype import AttributetypeAdmin
from gstudio.admin.attributespecification import AttributeSpecificationAdmin
from gstudio.admin.relationspecification import RelationSpecificationAdmin
from gstudio.admin.nodespecification import NodeSpecificationAdmin
from gstudio.admin.union import UnionAdmin
from gstudio.admin.complement import ComplementAdmin
from gstudio.admin.intersection import IntersectionAdmin 

from gstudio.admin.systemtype import SystemtypeAdmin
from gstudio.admin.processtype import ProcesstypeAdmin


admin.site.register(Objecttype, ObjecttypeAdmin)
admin.site.register(Metatype, MetatypeAdmin)
admin.site.register(Relationtype, RelationtypeAdmin)
admin.site.register(Relation, RelationAdmin)
admin.site.register(Attribute, AttributeAdmin)
admin.site.register(Attributetype, AttributetypeAdmin)

admin.site.register(Systemtype, SystemtypeAdmin)
admin.site.register(Processtype, ProcesstypeAdmin)
admin.site.register(AttributeSpecification, AttributeSpecificationAdmin)
admin.site.register(RelationSpecification, RelationSpecificationAdmin)
admin.site.register(NodeSpecification, NodeSpecificationAdmin)
admin.site.register(Union, UnionAdmin)
admin.site.register(Complement, ComplementAdmin)
admin.site.register(Intersection, IntersectionAdmin)




