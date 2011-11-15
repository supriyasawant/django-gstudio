"""Test cases for Attributeapp's quick attributetype"""
from django.test import TestCase
from django.contrib.auth.models import User

from attributeapp import settings
from attributeapp.models import Attributetype
from attributeapp.managers import DRAFT


class QuickAttributetypeTestCase(TestCase):
    """Test cases for quick_attributetype view"""
    urls = 'attributeapp.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_quick_attributetype(self):
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

        response = self.client.get('/quick_attributetype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_attributetype/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick_attributetype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_attributetype/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick_attributetype/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/attributeapp/attributetype/add/', 302)])
        response = self.client.post('/quick_attributetype/', {'title': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/attributeapp/attributetype/add/' \
                            '?tags=&title=test&sites=1&content=' \
                            '%3Cp%3E%3C%2Fp%3E&authors=2&slug=test', 302)])
        response = self.client.post('/quick_attributetype/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        attributetype = Attributetype.objects.get(title='test')
        self.assertEquals(response.redirect_chain,
                          [('http://testserver%s' % attributetype.get_absolute_url(),
                            302)])
        self.assertEquals(attributetype.status, DRAFT)
        self.assertEquals(attributetype.title, 'test')
        self.assertEquals(attributetype.tags, 'test')
        self.assertEquals(attributetype.content, '<p>Test content</p>')
