"""Settings of Attributeapp.plugins"""
import warnings

from django.conf import settings
from django.utils.importlib import import_module


HIDE_ATTRIBUTETYPE_MENU = getattr(settings, 'ATTRIBUTEAPP_HIDE_ATTRIBUTETYPE_MENU', True)

PLUGINS_TEMPLATES = getattr(settings, 'ATTRIBUTEAPP_PLUGINS_TEMPLATES', [])


APP_MENUS = []
DEFAULT_APP_MENUS = ['attributeapp.plugins.menu.AttributetypeMenu',
                     'attributeapp.plugins.menu.AttributeMenu',
                     'attributeapp.plugins.menu.TagMenu',
                     'attributeapp.plugins.menu.AuthorMenu']

for menu_string in getattr(settings, 'ATTRIBUTEAPP_APP_MENUS', DEFAULT_APP_MENUS):
    try:
        dot = menu_string.rindex('.')
        menu_module = menu_string[:dot]
        menu_name = menu_string[dot + 1:]
        APP_MENUS.append(getattr(import_module(menu_module), menu_name))
    except (ImportError, AttributeError):
        warnings.warn('%s menu cannot be imported' % menu_string,
                      RuntimeWarning)
