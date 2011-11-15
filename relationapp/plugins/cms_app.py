"""Applications hooks for relationapp.plugins"""
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from relationapp.plugins.settings import APP_MENUS


class RelationappApphook(CMSApp):
    """Relationapp's Apphook"""
    name = _('Relationapp App Hook')
    urls = ['relationapp.urls']
    menus = APP_MENUS

apphook_pool.register(RelationappApphook)
