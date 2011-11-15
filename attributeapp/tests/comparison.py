"""Test cases for Attributeapp's comparison"""
from django.test import TestCase

from attributeapp.models import Attributetype
from attributeapp.comparison import pearson_score
from attributeapp.comparison import VectorBuilder
from attributeapp.comparison import ClusteredModel


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
        params = {'title': 'My attributetype 1', 'content': 'My content 1',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-1'}
        Attributetype.objects.create(**params)
        params = {'title': 'My attributetype 2', 'content': 'My content 2',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-2'}
        Attributetype.objects.create(**params)
        cm = ClusteredModel(Attributetype.objects.all())
        self.assertEquals(cm.dataset().values(), ['1', '2'])
        cm = ClusteredModel(Attributetype.objects.all(),
                            ['title', 'excerpt', 'content'])
        self.assertEquals(cm.dataset().values(), ['My attributetype 1  My content 1',
                                                  'My attributetype 2  My content 2'])

    def test_vector_builder(self):
        vectors = VectorBuilder(Attributetype.objects.all(),
                                ['title', 'excerpt', 'content'])
        params = {'title': 'My attributetype 1', 'content':
                  'This is my first content',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-1'}
        Attributetype.objects.create(**params)
        params = {'title': 'My attributetype 2', 'content':
                  'My second attributetype',
                  'tags': 'attributeapp, test', 'slug': 'my-attributetype-2'}
        Attributetype.objects.create(**params)
        columns, dataset = vectors()
        self.assertEquals(columns, ['content', 'This', 'my', 'is', '1',
                                    'second', '2', 'first'])
        self.assertEquals(dataset.values(), [[1, 1, 1, 1, 1, 0, 0, 1],
                                             [0, 0, 0, 0, 0, 1, 1, 0]])
