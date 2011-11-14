"""Test cases for Attributeapp's Attribute"""
from django.test import TestCase
from django.contrib.sites.models import Site

from attributeapp.models import Attributetype
from attributeapp.models import Attribute
from attributeapp.managers import PUBLISHED


class AttributeTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.attributes = [Attribute.objects.create(title='Attribute 1',
                                                   slug='attribute-1'),
                           Attribute.objects.create(title='Attribute 2',
                                                   slug='attribute-2')]
        params = {'title': 'My attributetype',
                  'content': 'My content',
                  'tags': 'attributeapp, test',
                  'slug': 'my-attributetype'}

        self.attributetype = Attributetype.objects.create(**params)
        self.attributetype.attributes.add(*self.attributes)
        self.attributetype.sites.add(self.site)

    def test_attributetypes_published(self):
        attribute = self.attributes[0]
        self.assertEqual(attribute.attributetypes_published().count(), 0)
        self.attributetype.status = PUBLISHED
        self.attributetype.save()
        self.assertEqual(attribute.attributetypes_published().count(), 1)

        params = {'title': 'My second attributetype',
                  'content': 'My second content',
                  'tags': 'attributeapp, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-attributetype'}

        new_attributetype = Attributetype.objects.create(**params)
        new_attributetype.sites.add(self.site)
        new_attributetype.attributes.add(self.attributes[0])

        self.assertEqual(self.attributes[0].attributetypes_published().count(), 2)
        self.assertEqual(self.attributes[1].attributetypes_published().count(), 1)

    def test_attributetypes_tree_path(self):
        self.assertEqual(self.attributes[0].tree_path, 'attribute-1')
        self.assertEqual(self.attributes[1].tree_path, 'attribute-2')
        self.attributes[1].parent = self.attributes[0]
        self.attributes[1].save()
        self.assertEqual(self.attributes[1].tree_path, 'attribute-1/attribute-2')
