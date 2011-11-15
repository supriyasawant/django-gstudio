"""Applications hooks for attributeapp.plugins"""
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from attributeapp.plugins.settings import APP_MENUS


class AttributeappApphook(CMSApp):
    """Attributeapp's Apphook"""
    name = _('Attributeapp App Hook')
    urls = ['attributeapp.urls']
    menus = APP_MENUS

apphook_pool.register(AttributeappApphook)
