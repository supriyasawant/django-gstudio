"""Forms for Objectapp admin"""
from django import forms
from django.db.models import ManyToOneRel
from django.db.models import ManyToManyRel
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

from objectapp.models import GBObject
from objectapp.models import Objecttype
from objectapp.admin.widgets import TreeNodeChoiceField
from objectapp.admin.widgets import MPTTFilteredSelectMultiple
from objectapp.admin.widgets import MPTTModelMultipleChoiceField


class ObjecttypeAdminForm(forms.ModelForm):
    """Form for Objecttype's Admin"""
    parent = TreeNodeChoiceField(
        label=_('parent objecttype').capitalize(),
        required=False, empty_label=_('No parent objecttype'),
        queryset=Objecttype.tree.all())

    def __init__(self, *args, **kwargs):
        super(ObjecttypeAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToOneRel(Objecttype, 'id')
        self.fields['parent'].widget = RelatedFieldWidgetWrapper(
            self.fields['parent'].widget, rel, self.admin_site)

    def clean_parent(self):
        """Check if objecttype parent is not selfish"""
        data = self.cleaned_data['parent']
        if data == self.instance:
            raise forms.ValidationError(
                _('A objecttype cannot be a parent of itself.'))
        return data

    class Meta:
        """ObjecttypeAdminForm's Meta"""
        model = Objecttype


class GBObjectAdminForm(forms.ModelForm):
    """Form for GBObject's Admin"""

    objecttypes = MPTTModelMultipleChoiceField(
        label=_('Objecttypes'), required=False,
        queryset=Objecttype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('objecttypes'), False,
                                          attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(GBObjectAdminForm, self).__init__(*args, **kwargs)
        rel = ManyToManyRel(Objecttype, 'id')
        self.fields['objecttypes'].widget = RelatedFieldWidgetWrapper(
            self.fields['objecttypes'].widget, rel, self.admin_site)
        self.fields['sites'].initial = [Site.objects.get_current()]


    class Meta:
        """GBObjectAdminForm's Meta"""
        model = GBObject
