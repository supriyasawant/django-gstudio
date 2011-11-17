"""Menus for objectapp.plugins"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from menus.base import Modifier
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu

from objectapp.models import Gbobject
from objectapp.models import Author
from objectapp.models import Objecttype
from objectapp.managers import tags_published
from objectapp.plugins.settings import HIDE_GBOBJECT_MENU


class GbobjectMenu(CMSAttachMenu):
    """Menu for the gbobjects organized by archives dates"""
    name = _('Objectapp Gbobject Menu')

    def get_nodes(self, request):
        """Return menu's node for gbobjects"""
        nodes = []
        archives = []
        attributes = {'hidden': HIDE_GBOBJECT_MENU}
        for gbobject in Gbobject.published.all():
            year = gbobject.creation_date.strftime('%Y')
            month = gbobject.creation_date.strftime('%m')
            month_text = gbobject.creation_date.strftime('%b')
            day = gbobject.creation_date.strftime('%d')

            key_archive_year = 'year-%s' % year
            key_archive_month = 'month-%s-%s' % (year, month)
            key_archive_day = 'day-%s-%s-%s' % (year, month, day)

            if not key_archive_year in archives:
                nodes.append(NavigationNode(
                    year, reverse('objectapp_gbobject_archive_year', args=[year]),
                    key_archive_year, attr=attributes))
                archives.append(key_archive_year)

            if not key_archive_month in archives:
                nodes.append(NavigationNode(
                    month_text,
                    reverse('objectapp_gbobject_archive_month', args=[year, month]),
                    key_archive_month, key_archive_year,
                    attr=attributes))
                archives.append(key_archive_month)

            if not key_archive_day in archives:
                nodes.append(NavigationNode(
                    day, reverse('objectapp_gbobject_archive_day',
                                 args=[year, month, day]),
                    key_archive_day, key_archive_month,
                    attr=attributes))
                archives.append(key_archive_day)

            nodes.append(NavigationNode(gbobject.title, gbobject.get_absolute_url(),
                                        gbobject.pk, key_archive_day))
        return nodes


class ObjecttypeMenu(CMSAttachMenu):
    """Menu for the objecttypes"""
    name = _('Objectapp Objecttype Menu')

    def get_nodes(self, request):
        """Return menu's node for objecttypes"""
        nodes = []
        nodes.append(NavigationNode(_('Objecttypes'),
                                    reverse('objectapp_Objecttype_list'),
                                    'objecttypes'))
        for Objecttype in Objecttype.objects.all():
            nodes.append(NavigationNode(Objecttype.title,
                                        Objecttype.get_absolute_url(),
                                        Objecttype.pk, 'objecttypes'))
        return nodes


class AuthorMenu(CMSAttachMenu):
    """Menu for the authors"""
    name = _('Objectapp Author Menu')

    def get_nodes(self, request):
        """Return menu's node for authors"""
        nodes = []
        nodes.append(NavigationNode(_('Authors'),
                                    reverse('objectapp_author_list'),
                                    'authors'))
        for author in Author.published.all():
            nodes.append(NavigationNode(author.username,
                                        reverse('objectapp_author_detail',
                                                args=[author.username]),
                                        author.pk, 'authors'))
        return nodes


class TagMenu(CMSAttachMenu):
    """Menu for the tags"""
    name = _('Objectapp Tag Menu')

    def get_nodes(self, request):
        """Return menu's node for tags"""
        nodes = []
        nodes.append(NavigationNode(_('Tags'), reverse('objectapp_tag_list'),
                                    'tags'))
        for tag in tags_published():
            nodes.append(NavigationNode(tag.name,
                                        reverse('objectapp_tag_detail',
                                                args=[tag.name]),
                                        tag.pk, 'tags'))
        return nodes


class GbobjectModifier(Modifier):
    """Menu Modifier for gbobjects,
    hide the MenuGbobject in navigation, not in breadcrumbs"""

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """Modify nodes of a menu"""
        if breadcrumb:
            return nodes
        for node in nodes:
            if node.attr.get('hidden'):
                nodes.remove(node)
        return nodes


menu_pool.register_menu(GbobjectMenu)
menu_pool.register_menu(ObjecttypeMenu)
menu_pool.register_menu(AuthorMenu)
menu_pool.register_menu(TagMenu)
menu_pool.register_modifier(GbobjectModifier)
