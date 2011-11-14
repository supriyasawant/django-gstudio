"""Test cases for Attributeapp's signals"""
from django.test import TestCase

from attributeapp.models import Attributetype
from attributeapp.managers import DRAFT
from attributeapp.managers import PUBLISHED
from attributeapp.signals import disable_for_loaddata
from attributeapp.signals import ping_directories_handler
from attributeapp.signals import ping_external_urls_handler


class SignalsTestCase(TestCase):
    """Test cases for signals"""

    def test_disable_for_loaddata(self):
        self.top = 0

        @disable_for_loaddata
        def make_top():
            self.top += 1

        def call():
            return make_top()

        call()
        self.assertEquals(self.top, 1)
        # Okay the command is executed

    def test_ping_directories_handler(self):
        # Set up a stub around DirectoryPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        import attributeapp.ping
        from attributeapp import settings
        self.original_pinger = attributeapp.ping.DirectoryPinger
        attributeapp.ping.DirectoryPinger = fake_pinger

        params = {'title': 'My attributetype',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-attributetype'}
        attributetype = Attributetype.objects.create(**params)
        self.assertEquals(attributetype.is_visible, True)
        settings.PING_DIRECTORIES = ()
        ping_directories_handler('sender', **{'instance': attributetype})
        self.assertEquals(self.top, 0)
        settings.PING_DIRECTORIES = ('toto',)
        settings.SAVE_PING_DIRECTORIES = True
        ping_directories_handler('sender', **{'instance': attributetype})
        self.assertEquals(self.top, 1)
        attributetype.status = DRAFT
        ping_directories_handler('sender', **{'instance': attributetype})
        self.assertEquals(self.top, 1)

        # Remove stub
        attributeapp.ping.DirectoryPinger = self.original_pinger

    def test_ping_external_urls_handler(self):
        # Set up a stub around ExternalUrlsPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        import attributeapp.ping
        from attributeapp import settings
        self.original_pinger = attributeapp.ping.ExternalUrlsPinger
        attributeapp.ping.ExternalUrlsPinger = fake_pinger

        params = {'title': 'My attributetype',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-attributetype'}
        attributetype = Attributetype.objects.create(**params)
        self.assertEquals(attributetype.is_visible, True)
        settings.SAVE_PING_EXTERNAL_URLS = False
        ping_external_urls_handler('sender', **{'instance': attributetype})
        self.assertEquals(self.top, 0)
        settings.SAVE_PING_EXTERNAL_URLS = True
        ping_external_urls_handler('sender', **{'instance': attributetype})
        self.assertEquals(self.top, 1)
        attributetype.status = 0
        ping_external_urls_handler('sender', **{'instance': attributetype})
        self.assertEquals(self.top, 1)

        # Remove stub
        attributeapp.ping.ExternalUrlsPinger = self.original_pinger
