"""MetatypeAdmin for Gstudio"""
from django.contrib import admin
from django.core.urlresolvers import NoReverseMatch
from django.utils.translation import ugettext_lazy as _

from gstudio.admin.forms import AttributetypeAdminForm
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


class AttributetypeAdmin(reversion.VersionAdmin):

    fieldsets = ((_('Neighbourhood'), {'fields': ('title', 'content', 'parent',
                                            'image', 'slug','status')}),
                 (_('Attribute Definiton'), {'fields': ('subjecttype','applicablenodetypes','dataType'), 
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



