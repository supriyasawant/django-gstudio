"""Test cases for Objectapp's quick gbobject"""
from django.test import TestCase
from django.contrib.auth.models import User

from objectapp import settings
from objectapp.models import GBObject
from objectapp.managers import DRAFT


class QuickGBObjectTestCase(TestCase):
    """Test cases for quick_gbobject view"""
    urls = 'objectapp.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_quick_gbobject(self):
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

        response = self.client.get('/quick_gbobject/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_gbobject/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick_gbobject/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_gbobject/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick_gbobject/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/objectapp/gbobject/add/', 302)])
        response = self.client.post('/quick_gbobject/', {'title': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/objectapp/gbobject/add/' \
                            '?tags=&title=test&sites=1&content=' \
                            '%3Cp%3E%3C%2Fp%3E&authors=2&slug=test', 302)])
        response = self.client.post('/quick_gbobject/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        gbobject = GBObject.objects.get(title='test')
        self.assertEquals(response.redirect_chain,
                          [('http://testserver%s' % gbobject.get_absolute_url(),
                            302)])
        self.assertEquals(gbobject.status, DRAFT)
        self.assertEquals(gbobject.title, 'test')
        self.assertEquals(gbobject.tags, 'test')
        self.assertEquals(gbobject.content, '<p>Test content</p>')
