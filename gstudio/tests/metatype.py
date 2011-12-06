"""Test cases for Gstudio's Metatype"""
from django.test import TestCase
from django.contrib.sites.models import Site

from gstudio.models import Nodetype
from gstudio.models import Metatype
from gstudio.managers import PUBLISHED


class MetatypeTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.metatypes = [Metatype.objects.create(title='Metatype 1',
                                                   slug='metatype-1'),
                           Metatype.objects.create(title='Metatype 2',
                                                   slug='metatype-2')]
        params = {'title': 'My nodetype',
                  'content': 'My content',
                  'tags': 'gstudio, test',
                  'slug': 'my-nodetype'}

        self.nodetype = Nodetype.objects.create(**params)
        self.nodetype.metatypes.add(*self.metatypes)
        self.nodetype.sites.add(self.site)

    def test_nodetypes_published(self):
        metatype = self.metatypes[0]
        self.assertEqual(metatype.nodetypes_published().count(), 0)
        self.nodetype.status = PUBLISHED
        self.nodetype.save()
        self.assertEqual(metatype.nodetypes_published().count(), 1)

        params = {'title': 'My second nodetype',
                  'content': 'My second content',
                  'tags': 'gstudio, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-nodetype'}

        new_nodetype = Nodetype.objects.create(**params)
        new_nodetype.sites.add(self.site)
        new_nodetype.metatypes.add(self.metatypes[0])

        self.assertEqual(self.metatypes[0].nodetypes_published().count(), 2)
        self.assertEqual(self.metatypes[1].nodetypes_published().count(), 1)

    def test_nodetypes_tree_path(self):
        self.assertEqual(self.metatypes[0].tree_path, 'metatype-1')
        self.assertEqual(self.metatypes[1].tree_path, 'metatype-2')
        self.metatypes[1].parent = self.metatypes[0]
        self.metatypes[1].save()
        self.assertEqual(self.metatypes[1].tree_path, 'metatype-1/metatype-2')
