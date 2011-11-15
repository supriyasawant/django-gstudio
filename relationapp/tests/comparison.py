"""Test cases for Relationapp's comparison"""
from django.test import TestCase

from relationapp.models import Relationtype
from relationapp.comparison import pearson_score
from relationapp.comparison import VectorBuilder
from relationapp.comparison import ClusteredModel


class ComparisonTestCase(TestCase):
    """Test cases for comparison tools"""

    def test_pearson_score(self):
        self.assertEquals(pearson_score([42], [42]), 0.0)
        self.assertEquals(pearson_score([0, 1, 2], [0, 1, 2]), 0.0)
        self.assertEquals(pearson_score([0, 1, 3], [0, 1, 2]),
                          0.051316701949486232)
        self.assertEquals(pearson_score([0, 1, 2], [0, 1, 3]),
                          0.051316701949486232)

    def test_clustered_model(self):
        params = {'title': 'My relationtype 1', 'content': 'My content 1',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-1'}
        Relationtype.objects.create(**params)
        params = {'title': 'My relationtype 2', 'content': 'My content 2',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-2'}
        Relationtype.objects.create(**params)
        cm = ClusteredModel(Relationtype.objects.all())
        self.assertEquals(cm.dataset().values(), ['1', '2'])
        cm = ClusteredModel(Relationtype.objects.all(),
                            ['title', 'excerpt', 'content'])
        self.assertEquals(cm.dataset().values(), ['My relationtype 1  My content 1',
                                                  'My relationtype 2  My content 2'])

    def test_vector_builder(self):
        vectors = VectorBuilder(Relationtype.objects.all(),
                                ['title', 'excerpt', 'content'])
        params = {'title': 'My relationtype 1', 'content':
                  'This is my first content',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-1'}
        Relationtype.objects.create(**params)
        params = {'title': 'My relationtype 2', 'content':
                  'My second relationtype',
                  'tags': 'relationapp, test', 'slug': 'my-relationtype-2'}
        Relationtype.objects.create(**params)
        columns, dataset = vectors()
        self.assertEquals(columns, ['content', 'This', 'my', 'is', '1',
                                    'second', '2', 'first'])
        self.assertEquals(dataset.values(), [[1, 1, 1, 1, 1, 0, 0, 1],
                                             [0, 0, 0, 0, 0, 1, 1, 0]])
