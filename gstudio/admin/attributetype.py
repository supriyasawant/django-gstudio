"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.html import strip_tags
from django.utils.text import truncate_words
from django.core.urlresolvers import reverse, NoReverseMatch
from django.conf.urls.defaults import url
from django.conf.urls.defaults import patterns
from django.utils.translation import ugettext_lazy as _
from django.forms import Media

from django.conf import settings as project_settings

from gstudio.admin.forms import AttributetypeAdminForm
import reversion

from objectapp.models import Gbobject
from objectapp.models import Objecttype
from objectapp.models import System
from objectapp.models import Process
from objectapp.models import Systemtype
from gstudio.models import Edge
from gstudio.models import Node

from gstudio import settings

from objectapp.admin.widgets import TreeNodeChoiceField
from objectapp.admin.widgets import MPTTFilteredSelectMultiple
from objectapp.admin.widgets import MPTTModelMultipleChoiceField


class AttributetypeAdmin(reversion.VersionAdmin):
    form = AttributetypeAdminForm
    prepopulated_fields = {'slug': ('title', )}


    fieldsets = ((_('Attribute Definiton'), {'fields': ('title','subjecttype','applicablenodetypes','dataType','parent','slug','status') }),

                 (_('Content'), {'fields': ('content', 'image',), 
                                 'classes': ('collapse', 'collapse-closed')}),

                 
                  		   
                 (_('Dependency'), {'fields': ('priornode', 'posteriornode',), 
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Options'), {'fields': ('featured', 'excerpt', 'template',
                                            'related', 'authors',
                                            'creation_date',
                                            'start_publication',
                                            'end_publication'),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Privacy'), {'fields': ('password', 'login_required',),
                                 'classes': ('collapse', 'collapse-closed')}),
                 (_('Publication'), {'fields': ('tags', 
                                                'sites')}))

    def __init__(self, model, admin_site):
        self.form.admin_site = admin_site
        super(AttributetypeAdmin, self).__init__(model, admin_site)

    def get_tree_path(self, System):
            """Return the Objecttype's tree path in HTML"""
            try:
                return '<a href="%s" target="blank">/%s/</a>' % \
                   (Attributetype.get_absolute_url(), Attributetype.tree_path)
            except NoReverseMatch:
                return '/%s/' % Attributetype.tree_path
            get_tree_path.allow_tags = True
            get_tree_path.short_description = _('tree path')
    def _media(self):
        STATIC_URL = '%sgstudio/' % project_settings.STATIC_URL
        media = super(AttributetypeAdmin, self).media + Media(
            css={'all': ('%scss/jquery.autocomplete.css' % STATIC_URL,)},
            js=('%sjs/jquery.js' % STATIC_URL,
                '%sjs/jquery.bgiframe.js' % STATIC_URL,
                '%sjs/jquery.autocomplete.js' % STATIC_URL,
                reverse('admin:objectapp_gbobject_autocomplete_tags'),))

        if settings.WYSIWYG == 'wymeditor':
            media += Media(
                js=('%sjs/wymeditor/jquery.wymeditor.pack.js' % STATIC_URL,
                    '%sjs/wymeditor/plugins/hovertools/'
                    'jquery.wymeditor.hovertools.js' % STATIC_URL,
                    reverse('admin:objectapp_gbobject_wymeditor')))
        elif settings.WYSIWYG == 'tinymce':
            from tinymce.widgets import TinyMCE
            media += TinyMCE().media + Media(
                js=(reverse('tinymce-js', args=('admin/objectapp/gbobject',)),))
        elif settings.WYSIWYG == 'markitup':
            media += Media(
                js=('%sjs/markitup/jquery.markitup.js' % STATIC_URL,
                    '%sjs/markitup/sets/%s/set.js' % (
                        STATIC_URL, settings.MARKUP_LANGUAGE),
                    reverse('admin:objectapp_gbobject_markitup')),
                css={'all': (
                    '%sjs/markitup/skins/django/style.css' % STATIC_URL,
                    '%sjs/markitup/sets/%s/style.css' % (
                        STATIC_URL, settings.MARKUP_LANGUAGE))})
        return media
    media = property(_media)



