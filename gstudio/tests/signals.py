"""Test cases for Gstudio's signals"""
from django.test import TestCase

from gstudio.models import Objecttype
from gstudio.managers import DRAFT
from gstudio.managers import PUBLISHED
from gstudio.signals import disable_for_loaddata
from gstudio.signals import ping_directories_handler
from gstudio.signals import ping_external_urls_handler


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

        import gstudio.ping
        from gstudio import settings
        self.original_pinger = gstudio.ping.DirectoryPinger
        gstudio.ping.DirectoryPinger = fake_pinger

        params = {'title': 'My objecttype',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-objecttype'}
        objecttype = Objecttype.objects.create(**params)
        self.assertEquals(objecttype.is_visible, True)
        settings.PING_DIRECTORIES = ()
        ping_directories_handler('sender', **{'instance': objecttype})
        self.assertEquals(self.top, 0)
        settings.PING_DIRECTORIES = ('toto',)
        settings.SAVE_PING_DIRECTORIES = True
        ping_directories_handler('sender', **{'instance': objecttype})
        self.assertEquals(self.top, 1)
        objecttype.status = DRAFT
        ping_directories_handler('sender', **{'instance': objecttype})
        self.assertEquals(self.top, 1)

        # Remove stub
        gstudio.ping.DirectoryPinger = self.original_pinger

    def test_ping_external_urls_handler(self):
        # Set up a stub around ExternalUrlsPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        import gstudio.ping
        from gstudio import settings
        self.original_pinger = gstudio.ping.ExternalUrlsPinger
        gstudio.ping.ExternalUrlsPinger = fake_pinger

        params = {'title': 'My objecttype',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-objecttype'}
        objecttype = Objecttype.objects.create(**params)
        self.assertEquals(objecttype.is_visible, True)
        settings.SAVE_PING_EXTERNAL_URLS = False
        ping_external_urls_handler('sender', **{'instance': objecttype})
        self.assertEquals(self.top, 0)
        settings.SAVE_PING_EXTERNAL_URLS = True
        ping_external_urls_handler('sender', **{'instance': objecttype})
        self.assertEquals(self.top, 1)
        objecttype.status = 0
        ping_external_urls_handler('sender', **{'instance': objecttype})
        self.assertEquals(self.top, 1)

        # Remove stub
        gstudio.ping.ExternalUrlsPinger = self.original_pinger
