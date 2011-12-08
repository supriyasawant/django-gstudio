from gstudio.models import *
from objectapp.models import *
from reversion.models import *

mts = Metatype.objects.all()
ots = Objecttype.objects.all()
mt = Metatype.objects.get(title='concept class')
ot = Objecttype.objects.get(title='person')
rts = Relationtype.objects.all()
rt1 = Relationtype.objects.get(title='capital of')
rs= Relation.objects.all()
r1 = Relation.objects.get(relationtype=rt1.id)

o =Gbobject.objects.filter(title='Mumbai')
