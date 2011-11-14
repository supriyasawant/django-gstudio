"""Forms for Attributeapp admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.admin.widgets import TreeNodeChoiceField
from attributeapp.admin.widgets import MPTTFilteredSelectMultiple
from attributeapp.admin.widgets import MPTTModelMultipleChoiceField


class AttributeAdminForm(forms.ModelForm):
    """Form for Attribute's Admin"""
    parent = TreeNodeChoiceField(
        label=_('parent attribute').capitalize(),
        required=False, empty_label=_('No parent attribute'),
        queryset=Attribute.tree.all())

    def __init__(self, *args, **kwargs):
        super(AttributeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Attribute, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """Check if attribute parent is not selfish"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A attribute cannot be a parent of itself.'))
        return data

    class Meta:
        """AttributeAdminForm's Meta"""
        model = Attribute


class AttributetypeAdminForm(forms.ModelForm):
    """Form for Attributetype's Admin"""

    parent = TreeNodeChoiceField(
        label=_('parent attributetype').capitalize(),
        required=False, empty_label=_('No parent attributetype'),
        queryset=Attributetype.tree.all())

    attributes = MPTTModelMultipleChoiceField(
        label=_('Attributes'), required=False,
        queryset=Attribute.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('attributes'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(AttributetypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Attribute, 'id')
        self.fields['attributes'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributes'].widget, rel, self.admin_site)
        self.fields['sites'].initial = [Site.objects.get_current()]

    def clean_parent(self):
        """Check if an object does not become a parent of itself"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('An objectype cannot be parent of itself.'))
        return data

    class Meta:
        """AttributetypeAdminForm's Meta"""
        model = Attributetype
