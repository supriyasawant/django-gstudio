"""Unit tests for Gstudio"""
from unittest import TestSuite
from unittest import TestLoader
from django.conf import settings

from gstudio.tests.nodetype import NodetypeTestCase  # ~0.2s
from gstudio.tests.nodetype import NodetypeHtmlContentTestCase  # ~0.5s
from gstudio.tests.nodetype import NodetypeGetBaseModelTestCase
from gstudio.tests.signals import SignalsTestCase
from gstudio.tests.metatype import MetatypeTestCase
from gstudio.tests.admin import NodetypeAdminTestCase
from gstudio.tests.admin import MetatypeAdminTestCase
from gstudio.tests.managers import ManagersTestCase  # ~1.2s
from gstudio.tests.feeds import GstudioFeedsTestCase  # ~0.4s
from gstudio.tests.views import GstudioViewsTestCase  # ~1.5s ouch...
from gstudio.tests.views import GstudioCustomDetailViews  # ~0.3s
from gstudio.tests.pingback import PingBackTestCase  # ~0.3s
from gstudio.tests.metaweblog import MetaWeblogTestCase  # ~0.6s
from gstudio.tests.comparison import ComparisonTestCase
from gstudio.tests.quick_nodetype import QuickNodetypeTestCase  # ~0.4s
from gstudio.tests.sitemaps import GstudioSitemapsTestCase  # ~0.3s
from gstudio.tests.ping import DirectoryPingerTestCase
from gstudio.tests.ping import ExternalUrlsPingerTestCase
from gstudio.tests.templatetags import TemplateTagsTestCase  # ~0.4s
from gstudio.tests.moderator import NodetypeCommentModeratorTestCase  # ~0.1s
from gstudio.tests.spam_checker import SpamCheckerTestCase
from gstudio.tests.url_shortener import URLShortenerTestCase
from gstudio.signals import disconnect_gstudio_signals
# TOTAL ~ 6.6s


def suite():
    """Suite of TestCases for Django"""
    suite = TestSuite()
    loader = TestLoader()

    test_cases = (ManagersTestCase, NodetypeTestCase,
                  NodetypeGetBaseModelTestCase, SignalsTestCase,
                  NodetypeHtmlContentTestCase, MetatypeTestCase,
                  GstudioViewsTestCase, GstudioFeedsTestCase,
                  GstudioSitemapsTestCase, ComparisonTestCase,
                  DirectoryPingerTestCase, ExternalUrlsPingerTestCase,
                  TemplateTagsTestCase, QuickNodetypeTestCase,
                  URLShortenerTestCase, NodetypeCommentModeratorTestCase,
                  GstudioCustomDetailViews, SpamCheckerTestCase,
                  NodetypeAdminTestCase, MetatypeAdminTestCase)

    if 'django_xmlrpc' in settings.INSTALLED_APPS:
        test_cases += (PingBackTestCase, MetaWeblogTestCase)

    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite

disconnect_gstudio_signals()
