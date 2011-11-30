"""Forms for Gstudio admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.models import Relationtype
from gstudio.models import Relation
from gstudio.models import Attributetype
from gstudio.models import Attribute


from gstudio.models import Systemtype
from gstudio.models import Processtype

from gstudio.models import Edgetype
from gstudio.models import Edge
from gstudio.models import Node

from gstudio.admin.widgets import TreeNodeChoiceField
from gstudio.admin.widgets import MPTTFilteredSelectMultiple
from gstudio.admin.widgets import MPTTModelMultipleChoiceField

class RelationtypeAdminForm(forms.ModelForm):
    
    priornode = MPTTModelMultipleChoiceField(
        label=_('Priornodes'), required=False,
        queryset=Node.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('priornodes'), False,
                                          attrs={'rows': '10'}))
    posteriornode = MPTTModelMultipleChoiceField(
        label=_('Prosterior Nodes'), required=False,
        queryset=Node.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('prosteriornode'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(RelationtypeAdminForm, self).__init__(*args, **kwargs)
        pn = ManyToManyRel(Node, 'id')
       

        self.fields['priornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornode'].widget, pn, self.admin_site)
        self.fields['posteriornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornode'].widget, pn, self.admin_site)



    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Relationtype


class RelationAdminForm(forms.ModelForm):

    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Relation


class ProcesstypeAdminForm(forms.ModelForm):

    priornode = MPTTModelMultipleChoiceField(
        label=_('Priornodes'), required=False,
        queryset=Node.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('priornodes'), False,
                                          attrs={'rows': '10'}))
    posteriornode = MPTTModelMultipleChoiceField(
        label=_('Prosterior Nodes'), required=False,
        queryset=Node.objects.all(),
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
        pn = ManyToManyRel(Node, 'id')
        at = ManyToManyRel(Attributetype, 'id')
        rt = ManyToManyRel(Relationtype, 'id')
       

        self.fields['priornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornode'].widget, pn, self.admin_site)
        self.fields['posteriornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornode'].widget, pn, self.admin_site)
        self.fields['attributetype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributetype_set'].widget, at, self.admin_site)
        self.fields['relationtype_set'].widget = RelatedFieldWidgetWrapper(
            self.fields['relationtype_set'].widget, rt, self.admin_site)




    class Meta:
        """SystemAdminForm's Meta"""
        model = Processtype

class AttributetypeAdminForm(forms.ModelForm):
    priornode = MPTTModelMultipleChoiceField(
        label=_('Priornodes'), required=False,
        queryset=Node.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('priornodes'), False,
                                          attrs={'rows': '10'}))
    posteriornode = MPTTModelMultipleChoiceField(
        label=_('Prosterior Nodes'), required=False,
        queryset=Node.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('prosteriornode'), False,
                                          attrs={'rows': '10'}))
    def __init__(self, *args, **kwargs):
        super(AttributetypeAdminForm, self).__init__(*args, **kwargs)
        pn = ManyToManyRel(Node, 'id')
       

        self.fields['priornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornode'].widget, pn, self.admin_site)
        self.fields['posteriornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornode'].widget, pn, self.admin_site)


    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Attributetype


class AttributeAdminForm(forms.ModelForm):

    class Meta:
        """MetatypeAdminForm's Meta"""
        model = Attribute

        
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
        label=_('parent objecttype').capitalize(),
        required=False, empty_label=_('No parent objecttype'),
        queryset=Objecttype.tree.all())

    metatypes = MPTTModelMultipleChoiceField(
        label=_('Metatypes'), required=False,
        queryset=Metatype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('metatypes'), False,
                                          attrs={'rows': '10'}))
    priornode = MPTTModelMultipleChoiceField(
        label=_('priornodes'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('objecttypes'), False,
                                          attrs={'rows': '10'}))

    posteriornode = MPTTModelMultipleChoiceField(
        label=_('posteriornode'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('objecttypes'), False,
                                          attrs={'rows': '10'}))



    def __init__(self, *args, **kwargs):
        super(ObjecttypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Metatype, 'id')
        prior = ManyToManyRel(Objecttype,'id')
        post = ManyToManyRel(Objecttype,'id')
        self.fields['metatypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['metatypes'].widget, rel, self.admin_site)
        self.fields['priornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornode'].widget, prior, self.admin_site)
        self.fields['posteriornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornode'].widget, post, self.admin_site)


        self.fields['sites'].initial = [Site.objects.get_current()]

    def clean_parent(self):
        """Check if an object does not become a parent of itself"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('An objectype cannot be parent of itself.'))
        return data

    class Meta:
        """ObjecttypeAdminForm's Meta"""
        model = Objecttype

class SystemtypeAdminForm(forms.ModelForm):
    objecttypeset = MPTTModelMultipleChoiceField(
        label=_('Objecttypeset'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Objecttypesets'), False,
                                          attrs={'rows': '10'}))
    relationtypeset = MPTTModelMultipleChoiceField(
        label=_('Relationtypeset'), required=False,
        queryset=Relationtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Relationtypesets'), False,
                                          attrs={'rows': '10'}))
    attributetypeset = MPTTModelMultipleChoiceField(
        label=_('Attributetypeset'), required=False,
        queryset=Attributetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Attributetypesets'), False,
                                          attrs={'rows': '10'}))
    metatypeset = MPTTModelMultipleChoiceField(
        label=_('Metatypeset'), required=False,
        queryset=Metatype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('metatypesets'), False,
                                          attrs={'rows': '10'}))
    processtypeset = MPTTModelMultipleChoiceField(
        label=_('Processtypeset'), required=False,
        queryset=Processtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Processtypesets'), False,
                                          attrs={'rows': '10'}))

    priornode = MPTTModelMultipleChoiceField(
        label=_('priornodes'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('objecttypes'), False,
                                          attrs={'rows': '10'}))

    posteriornode = MPTTModelMultipleChoiceField(
        label=_('posteriornode'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('objecttypes'), False,
                                          attrs={'rows': '10'}))
    def __init__(self, *args, **kwargs):
        super(SystemtypeAdminForm, self).__init__(*args, **kwargs)
        ob = ManyToManyRel(Objecttype,'id')
        rl = ManyToManyRel(Relationtype,'id')
        att = ManyToManyRel(Attributetype,'id')
        mt = ManyToManyRel(Metatype,'id')
        ps = ManyToManyRel(Processtype,'id')
        prior = ManyToManyRel(Objecttype,'id')
        post = ManyToManyRel(Objecttype,'id')


        self.fields['objecttypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['objecttypeset'].widget, ob, self.admin_site)
        self.fields['relationtypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['relationtypeset'].widget, rl, self.admin_site)
        self.fields['attributetypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributetypeset'].widget, att, self.admin_site)
        self.fields['metatypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['metatypeset'].widget, mt, self.admin_site)
        self.fields['processtypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['processtypeset'].widget, ps, self.admin_site)
        self.fields['posteriornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornode'].widget, post, self.admin_site)
        self.fields['posteriornode'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornode'].widget, post, self.admin_site)



    class Meta:
        """SystemAdminForm's Meta"""
        model = Systemtype
