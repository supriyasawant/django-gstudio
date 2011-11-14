"""Unit tests for Relationapp"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from relationapp.tests.relationtype import RelationtypeTestCase  # ~0.2s
from relationapp.tests.relationtype import RelationtypeHtmlContentTestCase  # ~0.5s
from relationapp.tests.relationtype import RelationtypeGetBaseModelTestCase
from relationapp.tests.signals import SignalsTestCase
from relationapp.tests.relation import RelationTestCase
from relationapp.tests.admin import RelationtypeAdminTestCase
from relationapp.tests.admin import RelationAdminTestCase
from relationapp.tests.managers import ManagersTestCase  # ~1.2s
from relationapp.tests.feeds import RelationappFeedsTestCase  # ~0.4s
from relationapp.tests.views import RelationappViewsTestCase  # ~1.5s ouch...
from relationapp.tests.views import RelationappCustomDetailViews  # ~0.3s
from relationapp.tests.pingback import PingBackTestCase  # ~0.3s
from relationapp.tests.metaweblog import MetaWeblogTestCase  # ~0.6s
from relationapp.tests.comparison import ComparisonTestCase
from relationapp.tests.quick_relationtype import QuickRelationtypeTestCase  # ~0.4s
from relationapp.tests.sitemaps import RelationappSitemapsTestCase  # ~0.3s
from relationapp.tests.ping import DirectoryPingerTestCase
from relationapp.tests.ping import ExternalUrlsPingerTestCase
from relationapp.tests.templatetags import TemplateTagsTestCase  # ~0.4s
from relationapp.tests.moderator import RelationtypeCommentModeratorTestCase  # ~0.1s
from relationapp.tests.spam_checker import SpamCheckerTestCase
from relationapp.tests.url_shortener import URLShortenerTestCase
from relationapp.signals import disconnect_relationapp_signals
# TOTAL ~ 6.6s


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (ManagersTestCase, RelationtypeTestCase,
                  RelationtypeGetBaseModelTestCase, SignalsTestCase,
                  RelationtypeHtmlContentTestCase, RelationTestCase,
                  RelationappViewsTestCase, RelationappFeedsTestCase,
                  RelationappSitemapsTestCase, ComparisonTestCase,
                  DirectoryPingerTestCase, ExternalUrlsPingerTestCase,
                  TemplateTagsTestCase, QuickRelationtypeTestCase,
                  URLShortenerTestCase, RelationtypeCommentModeratorTestCase,
                  RelationappCustomDetailViews, SpamCheckerTestCase,
                  RelationtypeAdminTestCase, RelationAdminTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_relationapp_signals()
