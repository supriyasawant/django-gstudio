"""Test cases for Gstudio's comparison"""
from django.test import TestCase

from gstudio.models import Nodetype
from gstudio.comparison import pearson_score
from gstudio.comparison import VectorBuilder
from gstudio.comparison import ClusteredModel


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
        params = {'title': 'My nodetype 1', 'content': 'My content 1',
                  'tags': 'gstudio, test', 'slug': 'my-nodetype-1'}
        Nodetype.objects.create(**params)
        params = {'title': 'My nodetype 2', 'content': 'My content 2',
                  'tags': 'gstudio, test', 'slug': 'my-nodetype-2'}
        Nodetype.objects.create(**params)
        cm = ClusteredModel(Nodetype.objects.all())
        self.assertEquals(cm.dataset().values(), ['1', '2'])
        cm = ClusteredModel(Nodetype.objects.all(),
                            ['title', 'excerpt', 'content'])
        self.assertEquals(cm.dataset().values(), ['My nodetype 1  My content 1',
                                                  'My nodetype 2  My content 2'])

    def test_vector_builder(self):
        vectors = VectorBuilder(Nodetype.objects.all(),
                                ['title', 'excerpt', 'content'])
        params = {'title': 'My nodetype 1', 'content':
                  'This is my first content',
                  'tags': 'gstudio, test', 'slug': 'my-nodetype-1'}
        Nodetype.objects.create(**params)
        params = {'title': 'My nodetype 2', 'content':
                  'My second nodetype',
                  'tags': 'gstudio, test', 'slug': 'my-nodetype-2'}
        Nodetype.objects.create(**params)
        columns, dataset = vectors()
        self.assertEquals(columns, ['content', 'This', 'my', 'is', '1',
                                    'second', '2', 'first'])
        self.assertEquals(dataset.values(), [[1, 1, 1, 1, 1, 0, 0, 1],
                                             [0, 0, 0, 0, 0, 1, 1, 0]])
