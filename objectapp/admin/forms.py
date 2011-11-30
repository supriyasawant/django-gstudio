"""Forms for Objectapp admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

import reversion
from objectapp.models import Gbobject
from objectapp.models import Objecttype
from objectapp.models import System
from objectapp.models import Process
from objectapp.models import Systemtype
from gstudio.models import Edge
from gstudio.models import Node
from gstudio.models import Relation
from gstudio.models import Attribute
from gstudio.models import Processtype

from objectapp.admin.widgets import TreeNodeChoiceField
from objectapp.admin.widgets import MPTTFilteredSelectMultiple
from objectapp.admin.widgets import MPTTModelMultipleChoiceField


class ProcessAdminForm(forms.ModelForm):

    class Meta:
        """SystemAdminForm's Meta"""
        model = Process

class SystemAdminForm(forms.ModelForm):
    systemtypes = MPTTModelMultipleChoiceField(
        label=_('Systemtypes'), required=False,
        queryset=Systemtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('systemtypes'), False,
                                          attrs={'rows': '10'}))
    objectset = MPTTModelMultipleChoiceField(
        label=_('Objectset'), required=False,
        queryset=Gbobject.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Objectsets'), False,
                                          attrs={'rows': '10'}))
    relationset = MPTTModelMultipleChoiceField(
        label=_('Relationset'), required=False,
        queryset=Relation.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Relationsets'), False,
                                          attrs={'rows': '10'}))
    attributeset = MPTTModelMultipleChoiceField(
        label=_('Attributeset'), required=False,
        queryset=Attribute.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Attributesets'), False,
                                          attrs={'rows': '10'}))

    processset = MPTTModelMultipleChoiceField(
        label=_('Processset'), required=False,
        queryset=Processtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Processsets'), False,
                                          attrs={'rows': '10'}))
    systemset = MPTTModelMultipleChoiceField(
        label=_('Systemset'), required=False,
        queryset=System.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Systemsets'), False,
                                          attrs={'rows': '10'}))



    def __init__(self, *args, **kwargs):
        super(SystemAdminForm, self).__init__(*args, **kwargs)
        st = ManyToManyRel(Systemtype, 'id')
        os = ManyToManyRel(Gbobject, 'id')
        rs = ManyToManyRel(Relation, 'id')
        at = ManyToManyRel(Attribute, 'id')
        ps = ManyToManyRel(Processtype, 'id')
        ss = ManyToManyRel(System, 'id')

        self.fields['systemtypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['systemtypes'].widget, st, self.admin_site)
        self.fields['objectset'].widget = RelatedFieldWidgetWrapper(
            self.fields['objectset'].widget, os, self.admin_site)
        self.fields['relationset'].widget = RelatedFieldWidgetWrapper(
            self.fields['relationset'].widget, rs, self.admin_site)
        self.fields['attributeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributeset'].widget, at, self.admin_site)
        self.fields['processset'].widget = RelatedFieldWidgetWrapper(
            self.fields['processset'].widget, ps, self.admin_site)
        self.fields['systemset'].widget = RelatedFieldWidgetWrapper(
            self.fields['systemset'].widget, ss, self.admin_site)





    class Meta:
        """SystemAdminForm's Meta"""
        model = System



class ObjecttypeAdminForm(forms.ModelForm):
    """Form for Objecttype's Admin"""
    parent = TreeNodeChoiceField(
        label=_('parent Objecttype').capitalize(),
        required=False, empty_label=_('No parent Objecttype'),
        queryset=Objecttype.tree.all())

    def __init__(self, *args, **kwargs):
        super(ObjecttypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Objecttype, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """Check if Objecttype parent is not selfish"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A Objecttype cannot be parent of itself.'))
        return data

    class Meta:
        """ObjecttypeAdminForm's Meta"""
        model = Objecttype


class GbobjectAdminForm(forms.ModelForm):
    """Form for Gbobject's Admin"""
    objecttypes = MPTTModelMultipleChoiceField(
        label=_('Objecttypes'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('objecttypes'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(GbobjectAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Objecttype, 'id')
        self.fields['objecttypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['objecttypes'].widget, rel, self.admin_site)
        self.fields['sites'].initial = [Site.objects.get_current()]

    class Meta:
        """GbobjectAdminForm's Meta"""
        model = Gbobject
