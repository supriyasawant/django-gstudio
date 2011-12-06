"""Test cases for Gstudio's quick nodetype"""
from django.test import TestCase
from django.contrib.auth.models import User

from gstudio import settings
from gstudio.models import Nodetype
from gstudio.managers import DRAFT


class QuickNodetypeTestCase(TestCase):
    """Test cases for quick_nodetype view"""
    urls = 'gstudio.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_quick_nodetype(self):
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

        response = self.client.get('/quick_nodetype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_nodetype/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick_nodetype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_nodetype/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick_nodetype/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/nodetype/add/', 302)])
        response = self.client.post('/quick_nodetype/', {'title': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/gstudio/nodetype/add/' \
                            '?tags=&title=test&sites=1&content=' \
                            '%3Cp%3E%3C%2Fp%3E&authors=2&slug=test', 302)])
        response = self.client.post('/quick_nodetype/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        nodetype = Nodetype.objects.get(title='test')
        self.assertEquals(response.redirect_chain,
                          [('http://testserver%s' % nodetype.get_absolute_url(),
                            302)])
        self.assertEquals(nodetype.status, DRAFT)
        self.assertEquals(nodetype.title, 'test')
        self.assertEquals(nodetype.tags, 'test')
        self.assertEquals(nodetype.content, '<p>Test content</p>')
