"""Test cases for Relationapp's signals"""
from django.test import TestCase

from relationapp.models import Relationtype
from relationapp.managers import DRAFT
from relationapp.managers import PUBLISHED
from relationapp.signals import disable_for_loaddata
from relationapp.signals import ping_directories_handler
from relationapp.signals import ping_external_urls_handler


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

        import relationapp.ping
        from relationapp import settings
        self.original_pinger = relationapp.ping.DirectoryPinger
        relationapp.ping.DirectoryPinger = fake_pinger

        params = {'title': 'My relationtype',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-relationtype'}
        relationtype = Relationtype.objects.create(**params)
        self.assertEquals(relationtype.is_visible, True)
        settings.PING_DIRECTORIES = ()
        ping_directories_handler('sender', **{'instance': relationtype})
        self.assertEquals(self.top, 0)
        settings.PING_DIRECTORIES = ('toto',)
        settings.SAVE_PING_DIRECTORIES = True
        ping_directories_handler('sender', **{'instance': relationtype})
        self.assertEquals(self.top, 1)
        relationtype.status = DRAFT
        ping_directories_handler('sender', **{'instance': relationtype})
        self.assertEquals(self.top, 1)

        # Remove stub
        relationapp.ping.DirectoryPinger = self.original_pinger

    def test_ping_external_urls_handler(self):
        # Set up a stub around ExternalUrlsPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        import relationapp.ping
        from relationapp import settings
        self.original_pinger = relationapp.ping.ExternalUrlsPinger
        relationapp.ping.ExternalUrlsPinger = fake_pinger

        params = {'title': 'My relationtype',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-relationtype'}
        relationtype = Relationtype.objects.create(**params)
        self.assertEquals(relationtype.is_visible, True)
        settings.SAVE_PING_EXTERNAL_URLS = False
        ping_external_urls_handler('sender', **{'instance': relationtype})
        self.assertEquals(self.top, 0)
        settings.SAVE_PING_EXTERNAL_URLS = True
        ping_external_urls_handler('sender', **{'instance': relationtype})
        self.assertEquals(self.top, 1)
        relationtype.status = 0
        ping_external_urls_handler('sender', **{'instance': relationtype})
        self.assertEquals(self.top, 1)

        # Remove stub
        relationapp.ping.ExternalUrlsPinger = self.original_pinger
