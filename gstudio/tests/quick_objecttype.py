"""Test cases for Gstudio's quick objecttype"""
from django.test import TestCase
from django.contrib.auth.models import User

from gstudio import settings
from gstudio.models import Objecttype
from gstudio.managers import DRAFT


class QuickObjecttypeTestCase(TestCase):
    """Test cases for quick_objecttype view"""
    urls = 'gstudio.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_quick_objecttype(self):
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

        response = self.client.get('/quick_objecttype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_objecttype/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick_objecttype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_objecttype/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick_objecttype/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/objecttype/add/', 302)])
        response = self.client.post('/quick_objecttype/', {'title': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/objecttype/add/' \
                            '?tags=&title=test&sites=1&content=' \
                            '%3Cp%3E%3C%2Fp%3E&authors=2&slug=test', 302)])
        response = self.client.post('/quick_objecttype/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        objecttype = Objecttype.objects.get(title='test')
        self.assertEquals(response.redirect_chain,
                          [('http://testserver%s' % objecttype.get_absolute_url(),
                            302)])
        self.assertEquals(objecttype.status, DRAFT)
        self.assertEquals(objecttype.title, 'test')
        self.assertEquals(objecttype.tags, 'test')
        self.assertEquals(objecttype.content, '<p>Test content</p>')
