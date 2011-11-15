"""Test cases for Attributeapp's admin"""
from django.test import TestCase
from django.contrib.auth.models import User

from attributeapp import settings
from attributeapp.models import Attributetype
from attributeapp.models import Attribute


class AttributetypeAdminTestCase(TestCase):
    """Test case for Attributetype Admin"""
    urls = 'attributeapp.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        attribute_1 = Attribute.objects.create(title='Attribute 1', slug='cat-1')
        Attribute.objects.create(title='Attribute 2', slug='cat-2',
                                parent=attribute_1)

        self.client.login(username='admin', password='password')

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_attributetype_add_and_change(self):
        """Test the insertion of an Attributetype"""
        self.assertEquals(Attributetype.objects.count(), 0)
        post_data = {'title': u'New attributetype',
                     'template': u'attributeapp/attributetype_detail.html',
                     'creation_date_0': u'2011-01-01',
                     'creation_date_1': u'12:00:00',
                     'start_publication_0': u'2011-01-01',
                     'start_publication_1': u'12:00:00',
                     'end_publication_0': u'2042-03-15',
                     'end_publication_1': u'00:00:00',
                     'status': u'2',
                     'sites': u'1',
                     'content': u'My content'}

        response = self.client.post('/admin/attributeapp/attributetype/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Attributetype.objects.count(), 0)

        post_data.update({'slug': u'new-attributetype'})
        response = self.client.post('/admin/attributeapp/attributetype/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/attributeapp/attributetype/', 302)])
        self.assertEquals(Attributetype.objects.count(), 1)


class AttributeAdminTestCase(TestCase):
    """Test cases for Attribute Admin"""
    urls = 'attributeapp.tests.urls'

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_attribute_add_and_change(self):
        """Test the insertion of a Attribute, change error, and new insert"""
        self.assertEquals(Attribute.objects.count(), 0)
        post_data = {'title': u'New attribute',
                     'slug': u'new-attribute'}
        response = self.client.post('/admin/attributeapp/attribute/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/attributeapp/attribute/', 302)])
        self.assertEquals(Attribute.objects.count(), 1)

        post_data.update({'parent': u'1'})
        response = self.client.post('/admin/attributeapp/attribute/1/', post_data)
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/admin/attributeapp/attribute/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Attribute.objects.count(), 1)

        post_data.update({'slug': u'new-attribute-2'})
        response = self.client.post('/admin/attributeapp/attribute/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/attributeapp/attribute/', 302)])
        self.assertEquals(Attribute.objects.count(), 2)
