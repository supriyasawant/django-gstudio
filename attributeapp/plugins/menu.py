"""Menus for attributeapp.plugins"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from menus.base import Modifier
from menus.base import NavigationNode
from menus.menu_pool import menu_pool
from cms.menu_bases import CMSAttachMenu

from attributeapp.models import Attributetype
from attributeapp.models import Author
from attributeapp.models import Attribute
from attributeapp.managers import tags_published
from attributeapp.plugins.settings import HIDE_ATTRIBUTETYPE_MENU


class AttributetypeMenu(CMSAttachMenu):
    """Menu for the attributetypes organized by archives dates"""
    name = _('Attributeapp Attributetype Menu')

    def get_nodes(self, request):
        """Return menu's node for attributetypes"""
        nodes = []
        archives = []
        attributes = {'hidden': HIDE_ATTRIBUTETYPE_MENU}
        for attributetype in Attributetype.published.all():
            year = attributetype.creation_date.strftime('%Y')
            month = attributetype.creation_date.strftime('%m')
            month_text = attributetype.creation_date.strftime('%b')
            day = attributetype.creation_date.strftime('%d')

            key_archive_year = 'year-%s' % year
            key_archive_month = 'month-%s-%s' % (year, month)
            key_archive_day = 'day-%s-%s-%s' % (year, month, day)

            if not key_archive_year in archives:
                nodes.append(NavigationNode(
                    year, reverse('attributeapp_attributetype_archive_year', args=[year]),
                    key_archive_year, attr=attributes))
                archives.append(key_archive_year)

            if not key_archive_month in archives:
                nodes.append(NavigationNode(
                    month_text,
                    reverse('attributeapp_attributetype_archive_month', args=[year, month]),
                    key_archive_month, key_archive_year,
                    attr=attributes))
                archives.append(key_archive_month)

            if not key_archive_day in archives:
                nodes.append(NavigationNode(
                    day, reverse('attributeapp_attributetype_archive_day',
                                 args=[year, month, day]),
                    key_archive_day, key_archive_month,
                    attr=attributes))
                archives.append(key_archive_day)

            nodes.append(NavigationNode(attributetype.title, attributetype.get_absolute_url(),
                                        attributetype.pk, key_archive_day))
        return nodes


class AttributeMenu(CMSAttachMenu):
    """Menu for the attributes"""
    name = _('Attributeapp Attribute Menu')

    def get_nodes(self, request):
        """Return menu's node for attributes"""
        nodes = []
        nodes.append(NavigationNode(_('Attributes'),
                                    reverse('attributeapp_attribute_list'),
                                    'attributes'))
        for attribute in Attribute.objects.all():
            nodes.append(NavigationNode(attribute.title,
                                        attribute.get_absolute_url(),
                                        attribute.pk, 'attributes'))
        return nodes


class AuthorMenu(CMSAttachMenu):
    """Menu for the authors"""
    name = _('Attributeapp Author Menu')

    def get_nodes(self, request):
        """Return menu's node for authors"""
        nodes = []
        nodes.append(NavigationNode(_('Authors'),
                                    reverse('attributeapp_author_list'),
                                    'authors'))
        for author in Author.published.all():
            nodes.append(NavigationNode(author.username,
                                        reverse('attributeapp_author_detail',
                                                args=[author.username]),
                                        author.pk, 'authors'))
        return nodes


class TagMenu(CMSAttachMenu):
    """Menu for the tags"""
    name = _('Attributeapp Tag Menu')

    def get_nodes(self, request):
        """Return menu's node for tags"""
        nodes = []
        nodes.append(NavigationNode(_('Tags'), reverse('attributeapp_tag_list'),
                                    'tags'))
        for tag in tags_published():
            nodes.append(NavigationNode(tag.name,
                                        reverse('attributeapp_tag_detail',
                                                args=[tag.name]),
                                        tag.pk, 'tags'))
        return nodes


class AttributetypeModifier(Modifier):
    """Menu Modifier for attributetypes,
    hide the MenuAttributetype in navigation, not in breadcrumbs"""

    def modify(self, request, nodes, namespace, root_id, post_cut, breadcrumb):
        """Modify nodes of a menu"""
        if breadcrumb:
            return nodes
        for node in nodes:
            if node.attr.get('hidden'):
                nodes.remove(node)
        return nodes


menu_pool.register_menu(AttributetypeMenu)
menu_pool.register_menu(AttributeMenu)
menu_pool.register_menu(AuthorMenu)
menu_pool.register_menu(TagMenu)
menu_pool.register_modifier(AttributetypeModifier)
