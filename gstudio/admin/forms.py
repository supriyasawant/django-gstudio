"""Forms for Gstudio admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from gstudio.models import Nodetype
from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.models import Relationtype
from gstudio.models import Relation
from gstudio.models import Attributetype
from gstudio.models import Attribute
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




from gstudio.models import Systemtype
from gstudio.models import Processtype


from gstudio.admin.widgets import TreeNodeChoiceField
from gstudio.admin.widgets import MPTTFilteredSelectMultiple
from gstudio.admin.widgets import MPTTModelMultipleChoiceField

        
class MetatypeAdminForm(forms.ModelForm):
    """Form for Metatype's Admin"""
    parent = TreeNodeChoiceField(
        label=_('parent metatype').capitalize(),
        required=False, empty_label=_('No parent metatype'),
        queryset=Metatype.tree.all())

    def __init__(self, *args, **kwargs):
        super(MetatypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Metatype, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """Check if metatype parent is not selfish"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A metatype cannot be a parent of itself.'))
        return data

    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Metatype


class ObjecttypeAdminForm(forms.ModelForm):
    """Form for Objecttype's Admin"""

    parent = TreeNodeChoiceField(
        label=_('parent nodetype').capitalize(),
        required=False, empty_label=_('No parent nodetype'),
        queryset=Nodetype.tree.all())

    metatypes = MPTTModelMultipleChoiceField(
        label=_('Metatypes'), required=False,
        queryset=Metatype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('metatypes'), False,
                                          attrs={'rows': '10'}))
    priornodes = MPTTModelMultipleChoiceField(
        label=_('priornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('nodetypes'), False,
                                          attrs={'rows': '10'}))

    posteriornodes = MPTTModelMultipleChoiceField(
        label=_('posteriornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('nodetypes'), False,
                                          attrs={'rows': '10'}))



    def __init__(self, *args, **kwargs):
        super(ObjecttypeAdminForm, self).__init__(*args, **kwargs)
        meta = ManyToManyRel(Metatype, 'id')
        prior = ManyToManyRel(Nodetype,'id')
        post = ManyToManyRel(Nodetype,'id')
        self.fields['metatypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['metatypes'].widget, meta, self.admin_site)
        self.fields['priornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornodes'].widget, prior, self.admin_site)
        self.fields['posteriornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornodes'].widget, post, self.admin_site)



        self.fields['sites'].initial = [Site.objects.get_current()]

    def clean_parent(self):
        """Check if an object does not become a parent of itself"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('An objectype cannot be parent of itself.'))
        return data

    class Meta:
        """NodetypeAdminForm's Meta"""
        model = Objecttype


class RelationtypeAdminForm(forms.ModelForm):
    
    priornodes = MPTTModelMultipleChoiceField(
        label=_('Priornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('priornodes'), False,
                                          attrs={'rows': '10'}))
    posteriornodes = MPTTModelMultipleChoiceField(
        label=_('Prosterior Nodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('prosteriornode'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(RelationtypeAdminForm, self).__init__(*args, **kwargs)
        prior = ManyToManyRel(Nodetype, 'id')
        post = ManyToManyRel(Nodetype, 'id')

       

        self.fields['priornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornodes'].widget, prior, self.admin_site)
        self.fields['posteriornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornodes'].widget, post, self.admin_site)




    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Relationtype


class RelationAdminForm(forms.ModelForm):

    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Relation


class ProcesstypeAdminForm(forms.ModelForm):

    priornodes = MPTTModelMultipleChoiceField(
        label=_('Priornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('priornodes'), False,
                                          attrs={'rows': '10'}))
    posteriornodes = MPTTModelMultipleChoiceField(
        label=_('Prosterior Nodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('prosteriornode'), False,
                                          attrs={'rows': '10'}))
    attributetype_set = MPTTModelMultipleChoiceField(
        label=_('Attributetype Sets'), required=False,
        queryset=Attributetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Attributetype Set'), False,
                                          attrs={'rows': '10'}))
    relationtype_set = MPTTModelMultipleChoiceField(
        label=_('Relationtype Set'), required=False,
        queryset=Relationtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Relationtype Set'), False,
                                          attrs={'rows': '10'}))


    def __init__(self, *args, **kwargs):
        super(ProcesstypeAdminForm, self).__init__(*args, **kwargs)
        prior = ManyToManyRel(Nodetype, 'id')
        post = ManyToManyRel(Nodetype, 'id')
        atype = ManyToManyRel(Attributetype, 'id')
        rtype = ManyToManyRel(Relationtype, 'id')
       

        self.fields['priornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornodes'].widget, prior, self.admin_site)
        self.fields['posteriornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornodes'].widget, post, self.admin_site)
        self.fields['attributetype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributetype_set'].widget, atype, self.admin_site)
        self.fields['relationtype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['relationtype_set'].widget, rtype, self.admin_site)




    class Meta:
        """SystemAdminForm's Meta"""
        model = Processtype

class AttributetypeAdminForm(forms.ModelForm):
    priornodes = MPTTModelMultipleChoiceField(
        label=_('Priornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('priornodes'), False,
                                          attrs={'rows': '10'}))
    posteriornodes = MPTTModelMultipleChoiceField(
        label=_('Posterior Nodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('posteriornodes'), False,
                                          attrs={'rows': '10'}))
    def __init__(self, *args, **kwargs):
        super(AttributetypeAdminForm, self).__init__(*args, **kwargs)
        prior = ManyToManyRel(Nodetype, 'id')
        post = ManyToManyRel(Nodetype, 'id')
       

        self.fields['priornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornodes'].widget, prior, self.admin_site)
        self.fields['posteriornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornodes'].widget, post, self.admin_site)



    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Attributetype


class AttributeAdminForm(forms.ModelForm):

    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Attribute



class SystemtypeAdminForm(forms.ModelForm):
    nodetype_set = MPTTModelMultipleChoiceField(
        label=_('Nodetypeset'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Nodetypesets'), False,
                                          attrs={'rows': '10'}))
    relationtype_set = MPTTModelMultipleChoiceField(
        label=_('Relationtypeset'), required=False,
        queryset=Relationtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Relationtypesets'), False,
                                          attrs={'rows': '10'}))
    attributetype_set = MPTTModelMultipleChoiceField(
        label=_('Attributetypeset'), required=False,
        queryset=Attributetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Attributetypesets'), False,
                                          attrs={'rows': '10'}))
    metatype_set = MPTTModelMultipleChoiceField(
        label=_('Metatypeset'), required=False,
        queryset=Metatype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('metatypesets'), False,
                                          attrs={'rows': '10'}))
    processtype_set = MPTTModelMultipleChoiceField(
        label=_('Processtypeset'), required=False,
        queryset=Processtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Processtypesets'), False,
                                          attrs={'rows': '10'}))

    priornodes = MPTTModelMultipleChoiceField(
        label=_('priornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('nodetypes'), False,
                                          attrs={'rows': '10'}))

    posteriornodes = MPTTModelMultipleChoiceField(
        label=_('posteriornodes'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('nodetypes'), False,
                                          attrs={'rows': '10'}))
    def __init__(self, *args, **kwargs):
        super(SystemtypeAdminForm, self).__init__(*args, **kwargs)
        ot = ManyToManyRel(Nodetype,'id')
        rt = ManyToManyRel(Relationtype,'id')
        at = ManyToManyRel(Attributetype,'id')
        mt = ManyToManyRel(Metatype,'id')
        pt = ManyToManyRel(Processtype,'id')
        prior = ManyToManyRel(Nodetype,'id')
        post = ManyToManyRel(Nodetype,'id')

        self.fields['nodetype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['nodetype_set'].widget, ot, self.admin_site)
        self.fields['relationtype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['relationtype_set'].widget, rt, self.admin_site)
        self.fields['attributetype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributetype_set'].widget, at, self.admin_site)
        self.fields['metatype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['metatype_set'].widget, mt, self.admin_site)
        self.fields['processtype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['processtype_set'].widget, pt, self.admin_site)
        self.fields['priornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornodes'].widget, prior, self.admin_site)
        self.fields['posteriornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornodes'].widget, post, self.admin_site)




    class Meta:
        """SystemAdminForm's Meta"""
        model = Systemtype


class AttributeSpecificationAdminForm(forms.ModelForm):
    class Meta:
        model = AttributeSpecification

class RelationSpecificationAdminForm(forms.ModelForm):
    class Meta:
        model = RelationSpecification

class NodeSpecificationAdminForm(forms.ModelForm):
    class Meta:
        model = NodeSpecification

class UnionAdminForm(forms.ModelForm):
    class Meta:
        model = Union

class ComplementAdminForm(forms.ModelForm):
    class Meta:
        model = Complement

class IntersectionAdminForm(forms.ModelForm):
    class Meta:
        model = Intersection



class IntersectionAdminForm(forms.ModelForm):
    class Meta:
        model = Intersection

### Datatypes here ###

class AttributeCharfieldAdminForm(forms.ModelForm):
    class Meta:
        model = AttributeCharfield

class AttributeTextFieldAdminForm(forms.ModelForm):
    class Meta:
        model = AttributeTextField

class IntegerFieldAdminForm(forms.ModelForm):
    class Meta:
        model = IntegerField

class CommaSeparatedIntegerFieldAdminForm(forms.ModelForm):
    class Meta:
        model = CommaSeparatedIntegerField
class GbBigIntegerFieldAdminForm(forms.ModelForm):
    class Meta:
        model = GbBigIntegerField
class PositiveIntegerFieldAdminForm(forms.ModelForm):
    class Meta:
        model = PositiveIntegerField

class DecimalFieldAdminForm(forms.ModelForm):
    class Meta:
        model = DecimalField
class FloatFieldAdminForm(forms.ModelForm):
    class Meta:
        model = FloatField
class BooleanFieldAdminForm(forms.ModelForm):
    class Meta:
        model = BooleanField

class NullBooleanFieldAdminForm(forms.ModelForm):
    class Meta:
        model = NullBooleanField
class DateFieldAdminForm(forms.ModelForm):
    class Meta:
        model = DateField
class DateTimeFieldAdminForm(forms.ModelForm):
    class Meta:
        model = DateField

class TimeFieldAdminForm(forms.ModelForm):
    class Meta:
        model = TimeField

class EmailFieldAdminForm(forms.ModelForm):
    class Meta:
        model = EmailField
class FileFieldAdminForm(forms.ModelForm):
    class Meta:
        model = FileField
class FilePathFieldAdminForm(forms.ModelForm):
    class Meta:
        model = FilePathField
class ImageFieldAdminForm(forms.ModelForm):
    class Meta:
        model = ImageField

class URLFieldAdminForm(forms.ModelForm):
    class Meta:
        model = URLField
class IPAddressFieldAdminForm(forms.ModelForm):
    class Meta:
        model = IPAddressField










