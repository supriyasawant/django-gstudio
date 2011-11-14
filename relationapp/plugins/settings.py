"""Settings of Relationapp.plugins"""
import warnings

from django.conf import settings
from django.utils.importlib import import_module


HIDE_RELATIONTYPE_MENU = getattr(settings, 'RELATIONAPP_HIDE_RELATIONTYPE_MENU', True)

PLUGINS_TEMPLATES = getattr(settings, 'RELATIONAPP_PLUGINS_TEMPLATES', [])


APP_MENUS = []
DEFAULT_APP_MENUS = ['relationapp.plugins.menu.RelationtypeMenu',
                     'relationapp.plugins.menu.RelationMenu',
                     'relationapp.plugins.menu.TagMenu',
                     'relationapp.plugins.menu.AuthorMenu']

for menu_string in getattr(settings, 'RELATIONAPP_APP_MENUS', DEFAULT_APP_MENUS):
    try:
        dot = menu_string.rindex('.')
        menu_module = menu_string[:dot]
        menu_name = menu_string[dot + 1:]
        APP_MENUS.append(getattr(import_module(menu_module), menu_name))
    except (ImportError, AttributeError):
        warnings.warn('%s menu cannot be imported' % menu_string,
                      RuntimeWarning)
