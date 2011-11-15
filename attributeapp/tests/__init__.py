"""Unit tests for Attributeapp"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from attributeapp.tests.attributetype import AttributetypeTestCase  # ~0.2s
from attributeapp.tests.attributetype import AttributetypeHtmlContentTestCase  # ~0.5s
from attributeapp.tests.attributetype import AttributetypeGetBaseModelTestCase
from attributeapp.tests.signals import SignalsTestCase
from attributeapp.tests.attribute import AttributeTestCase
from attributeapp.tests.admin import AttributetypeAdminTestCase
from attributeapp.tests.admin import AttributeAdminTestCase
from attributeapp.tests.managers import ManagersTestCase  # ~1.2s
from attributeapp.tests.feeds import AttributeappFeedsTestCase  # ~0.4s
from attributeapp.tests.views import AttributeappViewsTestCase  # ~1.5s ouch...
from attributeapp.tests.views import AttributeappCustomDetailViews  # ~0.3s
from attributeapp.tests.pingback import PingBackTestCase  # ~0.3s
from attributeapp.tests.metaweblog import MetaWeblogTestCase  # ~0.6s
from attributeapp.tests.comparison import ComparisonTestCase
from attributeapp.tests.quick_attributetype import QuickAttributetypeTestCase  # ~0.4s
from attributeapp.tests.sitemaps import AttributeappSitemapsTestCase  # ~0.3s
from attributeapp.tests.ping import DirectoryPingerTestCase
from attributeapp.tests.ping import ExternalUrlsPingerTestCase
from attributeapp.tests.templatetags import TemplateTagsTestCase  # ~0.4s
from attributeapp.tests.moderator import AttributetypeCommentModeratorTestCase  # ~0.1s
from attributeapp.tests.spam_checker import SpamCheckerTestCase
from attributeapp.tests.url_shortener import URLShortenerTestCase
from attributeapp.signals import disconnect_attributeapp_signals
# TOTAL ~ 6.6s


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (ManagersTestCase, AttributetypeTestCase,
                  AttributetypeGetBaseModelTestCase, SignalsTestCase,
                  AttributetypeHtmlContentTestCase, AttributeTestCase,
                  AttributeappViewsTestCase, AttributeappFeedsTestCase,
                  AttributeappSitemapsTestCase, ComparisonTestCase,
                  DirectoryPingerTestCase, ExternalUrlsPingerTestCase,
                  TemplateTagsTestCase, QuickAttributetypeTestCase,
                  URLShortenerTestCase, AttributetypeCommentModeratorTestCase,
                  AttributeappCustomDetailViews, SpamCheckerTestCase,
                  AttributetypeAdminTestCase, AttributeAdminTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_attributeapp_signals()
