"""Settings of Gstudio.plugins"""
import warnings

from django.conf import settings
from django.utils.importlib import import_module


HIDE_OBJECTTYPE_MENU = getattr(settings, 'GSTUDIO_HIDE_OBJECTTYPE_MENU', True)

PLUGINS_TEMPLATES = getattr(settings, 'GSTUDIO_PLUGINS_TEMPLATES', [])


APP_MENUS = []
DEFAULT_APP_MENUS = ['gstudio.plugins.menu.ObjecttypeMenu',
                     'gstudio.plugins.menu.MetatypeMenu',
                     'gstudio.plugins.menu.TagMenu',
                     'gstudio.plugins.menu.AuthorMenu']

for menu_string in getattr(settings, 'GSTUDIO_APP_MENUS', DEFAULT_APP_MENUS):
    try:
        dot = menu_string.rindex('.')
        menu_module = menu_string[:dot]
        menu_name = menu_string[dot + 1:]
        APP_MENUS.append(getattr(import_module(menu_module), menu_name))
    except (ImportError, AttributeError):
        warnings.warn('%s menu cannot be imported' % menu_string,
                      RuntimeWarning)
