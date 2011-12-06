"""Test cases for Gstudio's admin"""
from django.test import TestCase
from django.contrib.auth.models import User

from gstudio import settings
from gstudio.models import Nodetype
from gstudio.models import Metatype


class NodetypeAdminTestCase(TestCase):
    """Test case for Nodetype Admin"""
    urls = 'gstudio.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        metatype_1 = Metatype.objects.create(title='Metatype 1', slug='cat-1')
        Metatype.objects.create(title='Metatype 2', slug='cat-2',
                                parent=metatype_1)

        self.client.login(username='admin', password='password')

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_nodetype_add_and_change(self):
        """Test the insertion of an Nodetype"""
        self.assertEquals(Nodetype.objects.count(), 0)
        post_data = {'title': u'New nodetype',
                     'template': u'gstudio/nodetype_detail.html',
                     'creation_date_0': u'2011-01-01',
                     'creation_date_1': u'12:00:00',
                     'start_publication_0': u'2011-01-01',
                     'start_publication_1': u'12:00:00',
                     'end_publication_0': u'2042-03-15',
                     'end_publication_1': u'00:00:00',
                     'status': u'2',
                     'sites': u'1',
                     'content': u'My content'}

        response = self.client.post('/admin/gstudio/nodetype/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Nodetype.objects.count(), 0)

        post_data.update({'slug': u'new-nodetype'})
        response = self.client.post('/admin/gstudio/nodetype/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/nodetype/', 302)])
        self.assertEquals(Nodetype.objects.count(), 1)


class MetatypeAdminTestCase(TestCase):
    """Test cases for Metatype Admin"""
    urls = 'gstudio.tests.urls'

    def setUp(self):
        User.objects.create_superuser('admin', 'admin@example.com', 'password')
        self.client.login(username='admin', password='password')

    def test_metatype_add_and_change(self):
        """Test the insertion of a Metatype, change error, and new insert"""
        self.assertEquals(Metatype.objects.count(), 0)
        post_data = {'title': u'New metatype',
                     'slug': u'new-metatype'}
        response = self.client.post('/admin/gstudio/metatype/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/metatype/', 302)])
        self.assertEquals(Metatype.objects.count(), 1)

        post_data.update({'parent': u'1'})
        response = self.client.post('/admin/gstudio/metatype/1/', post_data)
        self.assertEquals(response.status_code, 200)

        response = self.client.post('/admin/gstudio/metatype/add/', post_data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(Metatype.objects.count(), 1)

        post_data.update({'slug': u'new-metatype-2'})
        response = self.client.post('/admin/gstudio/metatype/add/',
                                    post_data, follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/metatype/', 302)])
        self.assertEquals(Metatype.objects.count(), 2)
