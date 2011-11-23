"""Test cases for Gstudio's Metatype"""
from django.test import TestCase
from django.contrib.sites.models import Site

from gstudio.models import Objecttype
from gstudio.models import Metatype
from gstudio.managers import PUBLISHED


class MetatypeTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.metatypes = [Metatype.objects.create(title='Metatype 1',
                                                   slug='metatype-1'),
                           Metatype.objects.create(title='Metatype 2',
                                                   slug='metatype-2')]
        params = {'title': 'My objecttype',
                  'content': 'My content',
                  'tags': 'gstudio, test',
                  'slug': 'my-objecttype'}

        self.objecttype = Objecttype.objects.create(**params)
        self.objecttype.metatypes.add(*self.metatypes)
        self.objecttype.sites.add(self.site)

    def test_nodes_published(self):
        metatype = self.metatypes[0]
        self.assertEqual(metatype.nodes_published().count(), 0)
        self.objecttype.status = PUBLISHED
        self.objecttype.save()
        self.assertEqual(metatype.nodes_published().count(), 1)

        params = {'title': 'My second objecttype',
                  'content': 'My second content',
                  'tags': 'gstudio, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-objecttype'}

        new_objecttype = Objecttype.objects.create(**params)
        new_objecttype.sites.add(self.site)
        new_objecttype.metatypes.add(self.metatypes[0])

        self.assertEqual(self.metatypes[0].nodes_published().count(), 2)
        self.assertEqual(self.metatypes[1].nodes_published().count(), 1)

    def test_objecttypes_tree_path(self):
        self.assertEqual(self.metatypes[0].tree_path, 'metatype-1')
        self.assertEqual(self.metatypes[1].tree_path, 'metatype-2')
        self.metatypes[1].parent = self.metatypes[0]
        self.metatypes[1].save()
        self.assertEqual(self.metatypes[1].tree_path, 'metatype-1/metatype-2')
