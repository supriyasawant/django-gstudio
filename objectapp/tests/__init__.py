"""Unit tests for Objectapp"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from objectapp.tests.gbobject import GBObjectTestCase  # ~0.2s
from objectapp.tests.gbobject import GBObjectHtmlContentTestCase  # ~0.5s
from objectapp.tests.gbobject import GBObjectGetBaseModelTestCase
from objectapp.tests.signals import SignalsTestCase
from objectapp.tests.objecttype import ObjecttypeTestCase
from objectapp.tests.admin import GBObjectAdminTestCase
from objectapp.tests.admin import ObjecttypeAdminTestCase
from objectapp.tests.managers import ManagersTestCase  # ~1.2s
from objectapp.tests.feeds import ObjectappFeedsTestCase  # ~0.4s
from objectapp.tests.views import ObjectappViewsTestCase  # ~1.5s ouch...
from objectapp.tests.views import ObjectappCustomDetailViews  # ~0.3s
from objectapp.tests.pingback import PingBackTestCase  # ~0.3s
from objectapp.tests.metaweblog import MetaWeblogTestCase  # ~0.6s
from objectapp.tests.comparison import ComparisonTestCase
from objectapp.tests.quick_gbobject import QuickGBObjectTestCase  # ~0.4s
from objectapp.tests.sitemaps import ObjectappSitemapsTestCase  # ~0.3s
from objectapp.tests.ping import DirectoryPingerTestCase
from objectapp.tests.ping import ExternalUrlsPingerTestCase
from objectapp.tests.templatetags import TemplateTagsTestCase  # ~0.4s
from objectapp.tests.moderator import GBObjectCommentModeratorTestCase  # ~0.1s
from objectapp.tests.spam_checker import SpamCheckerTestCase
from objectapp.tests.url_shortener import URLShortenerTestCase
from objectapp.signals import disconnect_objectapp_signals
# TOTAL ~ 6.6s


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (ManagersTestCase, GBObjectTestCase,
                  GBObjectGetBaseModelTestCase, SignalsTestCase,
                  GBObjectHtmlContentTestCase, ObjecttypeTestCase,
                  ObjectappViewsTestCase, ObjectappFeedsTestCase,
                  ObjectappSitemapsTestCase, ComparisonTestCase,
                  DirectoryPingerTestCase, ExternalUrlsPingerTestCase,
                  TemplateTagsTestCase, QuickGBObjectTestCase,
                  URLShortenerTestCase, GBObjectCommentModeratorTestCase,
                  ObjectappCustomDetailViews, SpamCheckerTestCase,
                  GBObjectAdminTestCase, ObjecttypeAdminTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_objectapp_signals()
