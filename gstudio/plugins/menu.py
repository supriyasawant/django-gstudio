"""Menus for gstudio.plugins"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from menus.base import Modifier
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu

from gstudio.models import Objecttype
from gstudio.models import Author
from gstudio.models import Metatype
from gstudio.managers import tags_published
from gstudio.plugins.settings import HIDE_OBJECTTYPE_MENU


class ObjecttypeMenu(CMSAttachMenu):
    """Menu for the objecttypes organized by archives dates"""
    name = _('Gstudio Objecttype Menu')

    def get_nodes(self, request):
        """Return menu's node for objecttypes"""
        nodes = []
        archives = []
        attributes = {'hidden': HIDE_OBJECTTYPE_MENU}
        for objecttype in Objecttype.published.all():
            year = objecttype.creation_date.strftime('%Y')
            month = objecttype.creation_date.strftime('%m')
            month_text = objecttype.creation_date.strftime('%b')
            day = objecttype.creation_date.strftime('%d')

            key_archive_year = 'year-%s' % year
            key_archive_month = 'month-%s-%s' % (year, month)
            key_archive_day = 'day-%s-%s-%s' % (year, month, day)

            if not key_archive_year in archives:
                nodes.append(NavigationNode(
                    year, reverse('gstudio_objecttype_archive_year', args=[year]),
                    key_archive_year, attr=attributes))
                archives.append(key_archive_year)

            if not key_archive_month in archives:
                nodes.append(NavigationNode(
                    month_text,
                    reverse('gstudio_objecttype_archive_month', args=[year, month]),
                    key_archive_month, key_archive_year,
                    attr=attributes))
                archives.append(key_archive_month)

            if not key_archive_day in archives:
                nodes.append(NavigationNode(
                    day, reverse('gstudio_objecttype_archive_day',
                                 args=[year, month, day]),
                    key_archive_day, key_archive_month,
                    attr=attributes))
                archives.append(key_archive_day)

            nodes.append(NavigationNode(objecttype.title, objecttype.get_absolute_url(),
                                        objecttype.pk, key_archive_day))
        return nodes


class MetatypeMenu(CMSAttachMenu):
    """Menu for the metatypes"""
    name = _('Gstudio Metatype Menu')

    def get_nodes(self, request):
        """Return menu's node for metatypes"""
        nodes = []
        nodes.append(NavigationNode(_('Metatypes'),
                                    reverse('gstudio_metatype_list'),
                                    'metatypes'))
        for metatype in Metatype.objects.all():
            nodes.append(NavigationNode(metatype.title,
                                        metatype.get_absolute_url(),
                                        metatype.pk, 'metatypes'))
        return nodes


class AuthorMenu(CMSAttachMenu):
    """Menu for the authors"""
    name = _('Gstudio Author Menu')

    def get_nodes(self, request):
        """Return menu's node for authors"""
        nodes = []
        nodes.append(NavigationNode(_('Authors'),
                                    reverse('gstudio_author_list'),
                                    'authors'))
        for author in Author.published.all():
            nodes.append(NavigationNode(author.username,
                                        reverse('gstudio_author_detail',
                                                args=[author.username]),
                                        author.pk, 'authors'))
        return nodes


class TagMenu(CMSAttachMenu):
    """Menu for the tags"""
    name = _('Gstudio Tag Menu')

    def get_nodes(self, request):
        """Return menu's node for tags"""
        nodes = []
        nodes.append(NavigationNode(_('Tags'), reverse('gstudio_tag_list'),
                                    'tags'))
        for tag in tags_published():
            nodes.append(NavigationNode(tag.name,
                                        reverse('gstudio_tag_detail',
                                                args=[tag.name]),
                                        tag.pk, 'tags'))
        return nodes


class ObjecttypeModifier(Modifier):
    """Menu Modifier for objecttypes,
    hide the MenuObjecttype in navigation, not in breadcrumbs"""

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """Modify nodes of a menu"""
        if breadcrumb:
            return nodes
        for node in nodes:
            if node.attr.get('hidden'):
                nodes.remove(node)
        return nodes


menu_pool.register_menu(ObjecttypeMenu)
menu_pool.register_menu(MetatypeMenu)
menu_pool.register_menu(AuthorMenu)
menu_pool.register_menu(TagMenu)
menu_pool.register_modifier(ObjecttypeModifier)
