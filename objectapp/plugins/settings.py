"""Settings of Objectapp.plugins"""
import warnings

from django.conf import settings
from django.utils.importlib import import_module


HIDE_GBOBJECT_MENU = getattr(settings, 'OBJECTAPP_HIDE_GBOBJECT_MENU', True)

PLUGINS_TEMPLATES = getattr(settings, 'OBJECTAPP_PLUGINS_TEMPLATES', [])


APP_MENUS = []
DEFAULT_APP_MENUS = ['objectapp.plugins.menu.GbobjectMenu',
                     'objectapp.plugins.menu.ObjecttypeMenu',
                     'objectapp.plugins.menu.TagMenu',
                     'objectapp.plugins.menu.AuthorMenu']

for menu_string in getattr(settings, 'OBJECTAPP_APP_MENUS', DEFAULT_APP_MENUS):
    try:
        dot = menu_string.rindex('.')
        menu_module = menu_string[:dot]
        menu_name = menu_string[dot + 1:]
        APP_MENUS.append(getattr(import_module(menu_module), menu_name))
    except (ImportError, AttributeError):
        warnings.warn('%s menu cannot be imported' % menu_string,
                      RuntimeWarning)
