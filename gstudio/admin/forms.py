"""Forms for Gstudio admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from gstudio.models import Objecttype
from gstudio.models import Metatype
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
        label=_('parent objecttype').capitalize(),
        required=False, empty_label=_('No parent objecttype'),
        queryset=Objecttype.tree.all())

    metatypes = MPTTModelMultipleChoiceField(
        label=_('Metatypes'), required=False,
        queryset=Metatype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('metatypes'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(ObjecttypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Metatype, 'id')
        self.fields['metatypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['metatypes'].widget, rel, self.admin_site)
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
