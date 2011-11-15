"""Forms for Relationapp admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.admin.widgets import TreeNodeChoiceField
from relationapp.admin.widgets import MPTTFilteredSelectMultiple
from relationapp.admin.widgets import MPTTModelMultipleChoiceField


class RelationAdminForm(forms.ModelForm):
    """Form for Relation's Admin"""
    parent = TreeNodeChoiceField(
        label=_('parent relation').capitalize(),
        required=False, empty_label=_('No parent relation'),
        queryset=Relation.tree.all())

    def __init__(self, *args, **kwargs):
        super(RelationAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Relation, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """Check if relation parent is not selfish"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A relation cannot be a parent of itself.'))
        return data

    class Meta:
        """RelationAdminForm's Meta"""
        model = Relation


class RelationtypeAdminForm(forms.ModelForm):
    """Form for Relationtype's Admin"""

    parent = TreeNodeChoiceField(
        label=_('parent relationtype').capitalize(),
        required=False, empty_label=_('No parent relationtype'),
        queryset=Relationtype.tree.all())

    relations = MPTTModelMultipleChoiceField(
        label=_('Relations'), required=False,
        queryset=Relation.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('relations'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(RelationtypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Relation, 'id')
        self.fields['relations'].widget = RelatedFieldWidgetWrapper(
            self.fields['relations'].widget, rel, self.admin_site)
        self.fields['sites'].initial = [Site.objects.get_current()]

    def clean_parent(self):
        """Check if an object does not become a parent of itself"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('An objectype cannot be parent of itself.'))
        return data

    class Meta:
        """RelationtypeAdminForm's Meta"""
        model = Relationtype
