"""Test cases for Relationapp's Relation"""
from django.test import TestCase
from django.contrib.sites.models import Site

from relationapp.models import Relationtype
from relationapp.models import Relation
from relationapp.managers import PUBLISHED


class RelationTestCase(TestCase):

    def setUp(self):
        self.site = Site.objects.get_current()
        self.relations = [Relation.objects.create(title='Relation 1',
                                                   slug='relation-1'),
                           Relation.objects.create(title='Relation 2',
                                                   slug='relation-2')]
        params = {'title': 'My relationtype',
                  'content': 'My content',
                  'tags': 'relationapp, test',
                  'slug': 'my-relationtype'}

        self.relationtype = Relationtype.objects.create(**params)
        self.relationtype.relations.add(*self.relations)
        self.relationtype.sites.add(self.site)

    def test_relationtypes_published(self):
        relation = self.relations[0]
        self.assertEqual(relation.relationtypes_published().count(), 0)
        self.relationtype.status = PUBLISHED
        self.relationtype.save()
        self.assertEqual(relation.relationtypes_published().count(), 1)

        params = {'title': 'My second relationtype',
                  'content': 'My second content',
                  'tags': 'relationapp, test',
                  'status': PUBLISHED,
                  'slug': 'my-second-relationtype'}

        new_relationtype = Relationtype.objects.create(**params)
        new_relationtype.sites.add(self.site)
        new_relationtype.relations.add(self.relations[0])

        self.assertEqual(self.relations[0].relationtypes_published().count(), 2)
        self.assertEqual(self.relations[1].relationtypes_published().count(), 1)

    def test_relationtypes_tree_path(self):
        self.assertEqual(self.relations[0].tree_path, 'relation-1')
        self.assertEqual(self.relations[1].tree_path, 'relation-2')
        self.relations[1].parent = self.relations[0]
        self.relations[1].save()
        self.assertEqual(self.relations[1].tree_path, 'relation-1/relation-2')
