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
    edgeset = MPTTModelMultipleChoiceField(
        label=_('Edgeset'), required=False,
        queryset=Edge.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('edgesets'), False,
                                          attrs={'rows': '10'}))
    nodeset = MPTTModelMultipleChoiceField(
        label=_('Nodeset'), required=False,
        queryset=Systemtype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('nodesets'), False,
                                          attrs={'rows': '10'}))
    systemset = MPTTModelMultipleChoiceField(
        label=_('Systemset'), required=False,
        queryset=System.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('systemset'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(SystemAdminForm, self).__init__(*args, **kwargs)
        st = ManyToManyRel(Systemtype, 'id')
        ed = ManyToManyRel(Edge, 'id')
        nd = ManyToManyRel(Node, 'id')
        ss = ManyToManyRel(System, 'id')

        self.fields['systemtypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['systemtypes'].widget, st, self.admin_site)
        self.fields['edgeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['edgeset'].widget, ed, self.admin_site)
        self.fields['nodeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['nodeset'].widget, nd, self.admin_site)
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
