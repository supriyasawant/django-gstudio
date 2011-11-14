"""Test cases for Relationapp's quick relationtype"""
from django.test import TestCase
from django.contrib.auth.models import User

from relationapp import settings
from relationapp.models import Relationtype
from relationapp.managers import DRAFT


class QuickRelationtypeTestCase(TestCase):
    """Test cases for quick_relationtype view"""
    urls = 'relationapp.tests.urls'

    def setUp(self):
        self.original_wysiwyg = settings.WYSIWYG
        settings.WYSIWYG = None

    def tearDown(self):
        settings.WYSIWYG = self.original_wysiwyg

    def test_quick_relationtype(self):
        User.objects.create_user('user', 'user@example.com', 'password')
        User.objects.create_superuser('admin', 'admin@example.com', 'password')

        response = self.client.get('/quick_relationtype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_relationtype/', 302)])
        self.client.login(username='user', password='password')
        response = self.client.get('/quick_relationtype/', follow=True)
        self.assertEquals(
            response.redirect_chain,
            [('http://testserver/accounts/login/?next=/quick_relationtype/', 302)])
        self.client.logout()
        self.client.login(username='admin', password='password')
        response = self.client.get('/quick_relationtype/', follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/relationapp/relationtype/add/', 302)])
        response = self.client.post('/quick_relationtype/', {'title': 'test'},
                                    follow=True)
        self.assertEquals(response.redirect_chain,
                          [('http://testserver/admin/relationapp/relationtype/add/' \
                            '?tags=&title=test&sites=1&content=' \
                            '%3Cp%3E%3C%2Fp%3E&authors=2&slug=test', 302)])
        response = self.client.post('/quick_relationtype/',
                                    {'title': 'test', 'tags': 'test',
                                     'content': 'Test content',
                                     'save_draft': ''}, follow=True)
        relationtype = Relationtype.objects.get(title='test')
        self.assertEquals(response.redirect_chain,
                          [('http://testserver%s' % relationtype.get_absolute_url(),
                            302)])
        self.assertEquals(relationtype.status, DRAFT)
        self.assertEquals(relationtype.title, 'test')
        self.assertEquals(relationtype.tags, 'test')
        self.assertEquals(relationtype.content, '<p>Test content</p>')
