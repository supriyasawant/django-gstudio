"""Menus for relationapp.plugins"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from menus.base import Modifier
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu

from relationapp.models import Relationtype
from relationapp.models import Author
from relationapp.models import Relation
from relationapp.managers import tags_published
from relationapp.plugins.settings import HIDE_RELATIONTYPE_MENU


class RelationtypeMenu(CMSAttachMenu):
    """Menu for the relationtypes organized by archives dates"""
    name = _('Relationapp Relationtype Menu')

    def get_nodes(self, request):
        """Return menu's node for relationtypes"""
        nodes = []
        archives = []
        attributes = {'hidden': HIDE_RELATIONTYPE_MENU}
        for relationtype in Relationtype.published.all():
            year = relationtype.creation_date.strftime('%Y')
            month = relationtype.creation_date.strftime('%m')
            month_text = relationtype.creation_date.strftime('%b')
            day = relationtype.creation_date.strftime('%d')

            key_archive_year = 'year-%s' % year
            key_archive_month = 'month-%s-%s' % (year, month)
            key_archive_day = 'day-%s-%s-%s' % (year, month, day)

            if not key_archive_year in archives:
                nodes.append(NavigationNode(
                    year, reverse('relationapp_relationtype_archive_year', args=[year]),
                    key_archive_year, attr=attributes))
                archives.append(key_archive_year)

            if not key_archive_month in archives:
                nodes.append(NavigationNode(
                    month_text,
                    reverse('relationapp_relationtype_archive_month', args=[year, month]),
                    key_archive_month, key_archive_year,
                    attr=attributes))
                archives.append(key_archive_month)

            if not key_archive_day in archives:
                nodes.append(NavigationNode(
                    day, reverse('relationapp_relationtype_archive_day',
                                 args=[year, month, day]),
                    key_archive_day, key_archive_month,
                    attr=attributes))
                archives.append(key_archive_day)

            nodes.append(NavigationNode(relationtype.title, relationtype.get_absolute_url(),
                                        relationtype.pk, key_archive_day))
        return nodes


class RelationMenu(CMSAttachMenu):
    """Menu for the relations"""
    name = _('Relationapp Relation Menu')

    def get_nodes(self, request):
        """Return menu's node for relations"""
        nodes = []
        nodes.append(NavigationNode(_('Relations'),
                                    reverse('relationapp_relation_list'),
                                    'relations'))
        for relation in Relation.objects.all():
            nodes.append(NavigationNode(relation.title,
                                        relation.get_absolute_url(),
                                        relation.pk, 'relations'))
        return nodes


class AuthorMenu(CMSAttachMenu):
    """Menu for the authors"""
    name = _('Relationapp Author Menu')

    def get_nodes(self, request):
        """Return menu's node for authors"""
        nodes = []
        nodes.append(NavigationNode(_('Authors'),
                                    reverse('relationapp_author_list'),
                                    'authors'))
        for author in Author.published.all():
            nodes.append(NavigationNode(author.username,
                                        reverse('relationapp_author_detail',
                                                args=[author.username]),
                                        author.pk, 'authors'))
        return nodes


class TagMenu(CMSAttachMenu):
    """Menu for the tags"""
    name = _('Relationapp Tag Menu')

    def get_nodes(self, request):
        """Return menu's node for tags"""
        nodes = []
        nodes.append(NavigationNode(_('Tags'), reverse('relationapp_tag_list'),
                                    'tags'))
        for tag in tags_published():
            nodes.append(NavigationNode(tag.name,
                                        reverse('relationapp_tag_detail',
                                                args=[tag.name]),
                                        tag.pk, 'tags'))
        return nodes


class RelationtypeModifier(Modifier):
    """Menu Modifier for relationtypes,
    hide the MenuRelationtype in navigation, not in breadcrumbs"""

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """Modify nodes of a menu"""
        if breadcrumb:
            return nodes
        for node in nodes:
            if node.attr.get('hidden'):
                nodes.remove(node)
        return nodes


menu_pool.register_menu(RelationtypeMenu)
menu_pool.register_menu(RelationMenu)
menu_pool.register_menu(AuthorMenu)
menu_pool.register_menu(TagMenu)
menu_pool.register_modifier(RelationtypeModifier)
