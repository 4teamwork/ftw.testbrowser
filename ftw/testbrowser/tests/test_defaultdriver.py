from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.compat import HAS_ZOPE4
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.testing import DEFAULT_TESTING
from ftw.testbrowser.testing import REQUESTS_TESTING
from ftw.testbrowser.tests import BrowserTestCase
from unittest import skipIf


class TestDefaultDriver(BrowserTestCase):
    layer = DEFAULT_TESTING

    def test_lib_requests_without_zopeapp(self):
        browser = Browser()
        browser.default_driver = LIB_REQUESTS
        with browser:
            self.assertEqual(LIB_REQUESTS, browser.get_driver().LIBRARY_NAME)

    @skipIf(HAS_ZOPE4, 'Mechanize is not available for Zope 4')
    def test_lib_mechanize_without_zopeapp(self):
        browser = Browser()
        browser.default_driver = LIB_MECHANIZE
        with browser:
            self.assertEqual(LIB_MECHANIZE, browser.get_driver().LIBRARY_NAME)

    def test_lib_requests_with_zopeapp(self):
        browser = Browser()
        browser.default_driver = LIB_REQUESTS
        with browser(self.layer['app']):
            self.assertEqual(LIB_REQUESTS, browser.get_driver().LIBRARY_NAME)

    @skipIf(HAS_ZOPE4, 'Mechanize is not available for Zope 4')
    def test_lib_mechanize_with_zopeapp(self):
        browser = Browser()
        browser.default_driver = LIB_MECHANIZE
        with browser(self.layer['app']):
            self.assertEqual(LIB_MECHANIZE, browser.get_driver().LIBRARY_NAME)


class TestSwitchToRequestDriver(BrowserTestCase):
    layer = REQUESTS_TESTING

    @skipIf(HAS_ZOPE4, 'Mechanize is not available for Zope 4')
    @browsing
    def test_open_supports_choosing_mechanize_when_doing_request(self, browser):
        browser.open(library=LIB_MECHANIZE)
        self.assertEqual('MechanizeDriver',
                         type(browser.get_driver()).__name__)

    @browsing
    def test_open_supports_choosing_requests_when_doing_request(self, browser):
        browser.open(library=LIB_REQUESTS)
        self.assertEqual('RequestsDriver',
                         type(browser.get_driver()).__name__)

    @skipIf(HAS_ZOPE4, 'Mechanize is not available for Zope 4')
    @browsing
    def test_visit_supports_choosing_mechanize_when_doing_request(self, browser):
        browser.visit(library=LIB_MECHANIZE)
        self.assertEqual('MechanizeDriver',
                         type(browser.get_driver()).__name__)

    @browsing
    def test_visit_supports_choosing_requests_when_doing_request(self, browser):
        browser.visit(library=LIB_REQUESTS)
        self.assertEqual('RequestsDriver',
                         type(browser.get_driver()).__name__)
