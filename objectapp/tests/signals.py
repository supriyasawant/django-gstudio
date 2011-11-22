"""Test cases for Objectapp's signals"""
from django.test import TestCase

from objectapp.models import Gbobject
from objectapp.managers import DRAFT
from objectapp.managers import PUBLISHED
from objectapp.signals import disable_for_loaddata
from objectapp.signals import ping_directories_handler
from objectapp.signals import ping_external_urls_handler


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

        import objectapp.ping
        from objectapp import settings
        self.original_pinger = objectapp.ping.DirectoryPinger
        objectapp.ping.DirectoryPinger = fake_pinger

        params = {'title': 'My gbobject',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-gbobject'}
        gbobject = Gbobject.objects.create(**params)
        self.assertEquals(gbobject.is_visible, True)
        settings.PING_DIRECTORIES = ()
        ping_directories_handler('sender', **{'instance': gbobject})
        self.assertEquals(self.top, 0)
        settings.PING_DIRECTORIES = ('toto',)
        settings.SAVE_PING_DIRECTORIES = True
        ping_directories_handler('sender', **{'instance': gbobject})
        self.assertEquals(self.top, 1)
        gbobject.status = DRAFT
        ping_directories_handler('sender', **{'instance': gbobject})
        self.assertEquals(self.top, 1)

        # Remove stub
        objectapp.ping.DirectoryPinger = self.original_pinger

    def test_ping_external_urls_handler(self):
        # Set up a stub around ExternalUrlsPinger
        self.top = 0

        def fake_pinger(*ka, **kw):
            self.top += 1

        import objectapp.ping
        from objectapp import settings
        self.original_pinger = objectapp.ping.ExternalUrlsPinger
        objectapp.ping.ExternalUrlsPinger = fake_pinger

        params = {'title': 'My gbobject',
                  'content': 'My content',
                  'status': PUBLISHED,
                  'slug': 'my-gbobject'}
        gbobject = Gbobject.objects.create(**params)
        self.assertEquals(gbobject.is_visible, True)
        settings.SAVE_PING_EXTERNAL_URLS = False
        ping_external_urls_handler('sender', **{'instance': gbobject})
        self.assertEquals(self.top, 0)
        settings.SAVE_PING_EXTERNAL_URLS = True
        ping_external_urls_handler('sender', **{'instance': gbobject})
        self.assertEquals(self.top, 1)
        gbobject.status = 0
        ping_external_urls_handler('sender', **{'instance': gbobject})
        self.assertEquals(self.top, 1)

        # Remove stub
        objectapp.ping.ExternalUrlsPinger = self.original_pinger
