"""Test cases for Relationapp's admin"""
from django.test import TestCase
from django.contrib.auth.models import User

from relationapp import settings
from relationapp.models import Relationtype
from relationapp.models import Relation


class RelationtypeAdminTestCase(TestCase):
    """Test case for Relationtype Admin"""
    urls = 'relationapp.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        relation_1 = Relation.objects.create(title='Relation 1', slug='cat-1')
        Relation.objects.create(title='Relation 2', slug='cat-2',
                                parent=relation_1)

        self.client.login(username='admin', password='password')

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_relationtype_add_and_change(self):
        """Test the insertion of an Relationtype"""
        self.assertEquals(Relationtype.objects.count(), 0)
        post_data = {'title': u'New relationtype',
                     'template': u'relationapp/relationtype_detail.html',
                     'creation_date_0': u'2011-01-01',
                     'creation_date_1': u'12:00:00',
                     'start_publication_0': u'2011-01-01',
                     'start_publication_1': u'12:00:00',
                     'end_publication_0': u'2042-03-15',
                     'end_publication_1': u'00:00:00',
                     'status': u'2',
                     'sites': u'1',
                     'content': u'My content'}

        response = self.client.post('/admin/relationapp/relationtype/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Relationtype.objects.count(), 0)

        post_data.update({'slug': u'new-relationtype'})
        response = self.client.post('/admin/relationapp/relationtype/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/relationapp/relationtype/', 302)])
        self.assertEquals(Relationtype.objects.count(), 1)


class RelationAdminTestCase(TestCase):
    """Test cases for Relation Admin"""
    urls = 'relationapp.tests.urls'

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_relation_add_and_change(self):
        """Test the insertion of a Relation, change error, and new insert"""
        self.assertEquals(Relation.objects.count(), 0)
        post_data = {'title': u'New relation',
                     'slug': u'new-relation'}
        response = self.client.post('/admin/relationapp/relation/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/relationapp/relation/', 302)])
        self.assertEquals(Relation.objects.count(), 1)

        post_data.update({'parent': u'1'})
        response = self.client.post('/admin/relationapp/relation/1/', post_data)
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/admin/relationapp/relation/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Relation.objects.count(), 1)

        post_data.update({'slug': u'new-relation-2'})
        response = self.client.post('/admin/relationapp/relation/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/relationapp/relation/', 302)])
        self.assertEquals(Relation.objects.count(), 2)
