"""Test cases for Objectapp's Objecttype"""
from django.test import TestCase
from django.contrib.sites.models import Site

from objectapp.models import GBObject
from objectapp.models import Objecttype
from objectapp.managers import PUBLISHED


class ObjecttypeTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.objecttypes = [Objecttype.objects.create(title='Objecttype 1',
                                                   slug='objecttype-1'),
                           Objecttype.objects.create(title='Objecttype 2',
                                                   slug='objecttype-2')]
        params = {'title': 'My gbobject',
                  'content': 'My content',
                  'tags': 'objectapp, test',
                  'slug': 'my-gbobject'}

        self.gbobject = GBObject.objects.create(**params)
        self.gbobject.objecttypes.add(*self.objecttypes)
        self.gbobject.sites.add(self.site)

    def test_gbobjects_published(self):
        objecttype = self.objecttypes[0]
        self.assertEqual(objecttype.gbobjects_published().count(), 0)
        self.gbobject.status = PUBLISHED
        self.gbobject.save()
        self.assertEqual(objecttype.gbobjects_published().count(), 1)

        params = {'title': 'My second gbobject',
                  'content': 'My second content',
                  'tags': 'objectapp, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-gbobject'}

        new_gbobject = GBObject.objects.create(**params)
        new_gbobject.sites.add(self.site)
        new_gbobject.objecttypes.add(self.objecttypes[0])

        self.assertEqual(self.objecttypes[0].gbobjects_published().count(), 2)
        self.assertEqual(self.objecttypes[1].gbobjects_published().count(), 1)

    def test_gbobjects_tree_path(self):
        self.assertEqual(self.objecttypes[0].tree_path, 'objecttype-1')
        self.assertEqual(self.objecttypes[1].tree_path, 'objecttype-2')
        self.objecttypes[1].parent = self.objecttypes[0]
        self.objecttypes[1].save()
        self.assertEqual(self.objecttypes[1].tree_path, 'objecttype-1/objecttype-2')
