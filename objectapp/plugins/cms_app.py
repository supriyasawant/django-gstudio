"""Applications hooks for objectapp.plugins"""
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from objectapp.plugins.settings import APP_MENUS


class ObjectappApphook(CMSApp):
    """Objectapp's Apphook"""
    name = _('Objectapp App Hook')
    urls = ['objectapp.urls']
    menus = APP_MENUS

apphook_pool.register(ObjectappApphook)
