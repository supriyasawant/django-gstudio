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
    nodetypeset = MPTTModelMultipleChoiceField(
        label=_('Nodetypeset'), required=False,
        queryset=Nodetype.objects.all(),
        widget=MPTTFilteredSelectMultiple(_('Nodetypesets'), False,
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

        self.fields['nodetypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['nodetypeset'].widget, ot, self.admin_site)
        self.fields['relationtypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['relationtypeset'].widget, rt, self.admin_site)
        self.fields['attributetypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['attributetypeset'].widget, at, self.admin_site)
        self.fields['metatypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['metatypeset'].widget, mt, self.admin_site)
        self.fields['processtypeset'].widget = RelatedFieldWidgetWrapper(
            self.fields['processtypeset'].widget, pt, self.admin_site)
        self.fields['priornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['priornodes'].widget, prior, self.admin_site)
        self.fields['posteriornodes'].widget = RelatedFieldWidgetWrapper(
            self.fields['posteriornodes'].widget, post, self.admin_site)



    class Meta:
        """SystemAdminForm's Meta"""
        model = Systemtype
