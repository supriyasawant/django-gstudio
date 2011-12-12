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
from gstudio.models import AttributeCharfield
from gstudio.models import AttributeTextField
from gstudio.models import IntegerField
from gstudio.models import CommaSeparatedIntegerField
from gstudio.models import GbBigIntegerField
from gstudio.models import PositiveIntegerField
from gstudio.models import DecimalField
from gstudio.models import FloatField 
from gstudio.models import BooleanField
from gstudio.models import NullBooleanField
from gstudio.models import DateField
from gstudio.models import DateTimeField
from gstudio.models import TimeField
from gstudio.models import EmailField
from gstudio.models import FileField
from gstudio.models import FilePathField
from gstudio.models import ImageField
from gstudio.models import URLField
from gstudio.models import IPAddressField

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
from gstudio.admin.attributecharfield import AttributeCharfieldAdmin 
from gstudio.admin.attributetextfield import AttributeTextFieldAdmin
from gstudio.admin.integerfield import IntegerFieldAdmin
from gstudio.admin.commaseparatedintegerfield import CommaSeparatedIntegerFieldAdmin
from gstudio.admin.bigintegerfield import GbBigIntegerFieldAdmin
from gstudio.admin.positiveintegerfield import PositiveIntegerFieldAdmin
from gstudio.admin.decimalfield import DecimalFieldAdmin
from gstudio.admin.floatfield import FloatFieldAdmin
from gstudio.admin.booleanfield import BooleanFieldAdmin
from gstudio.admin.nullbooleanfield import NullBooleanFieldAdmin
from gstudio.admin.datefield import DateFieldAdmin
from gstudio.admin.datetimefield import DateTimeFieldAdmin
from gstudio.admin.timefield import TimeFieldAdmin
from gstudio.admin.emailfield import EmailFieldAdmin
from gstudio.admin.filefield import FileFieldAdmin
from gstudio.admin.filepathfield import FilePathFieldAdmin
from gstudio.admin.imagefield import ImageFieldAdmin
from gstudio.admin.urlfield import URLFieldAdmin
from gstudio.admin.ipaddressfield import IPAddressFieldAdmin





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

admin.site.register(AttributeCharfield,AttributeCharfieldAdmin)
admin.site.register(AttributeTextField,AttributeTextFieldAdmin)
admin.site.register(IntegerField,IntegerFieldAdmin)
admin.site.register(CommaSeparatedIntegerField,CommaSeparatedIntegerFieldAdmin)
admin.site.register(GbBigIntegerField,GbBigIntegerFieldAdmin)
admin.site.register(PositiveIntegerField,PositiveIntegerFieldAdmin)
admin.site.register(DecimalField,DecimalFieldAdmin)
admin.site.register(FloatField,FloatFieldAdmin)  
admin.site.register(BooleanField,BooleanFieldAdmin)
admin.site.register(NullBooleanField,NullBooleanFieldAdmin)
admin.site.register(DateField,DateFieldAdmin)
admin.site.register(DateTimeField,DateTimeFieldAdmin)
admin.site.register(TimeField,TimeFieldAdmin)
admin.site.register(EmailField,EmailFieldAdmin)
admin.site.register(FileField,FileFieldAdmin)
admin.site.register(FilePathField,FilePathFieldAdmin)
admin.site.register(ImageField,ImageFieldAdmin)
admin.site.register(URLField,URLFieldAdmin)
admin.site.register(IPAddressField,IPAddressFieldAdmin)




















