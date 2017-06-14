from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.testing import DEFAULT_TESTING
from ftw.testbrowser.testing import REQUESTS_TESTING
from ftw.testbrowser.tests import BrowserTestCase


class TestDefaultDriver(BrowserTestCase):
    layer = DEFAULT_TESTING

    def test_library_constants_without_zopeapp(self):
        browser = Browser()

        browser.default_driver = LIB_REQUESTS
        with browser:
            self.assertEquals(LIB_REQUESTS, browser.get_driver().LIBRARY_NAME)

        browser.default_driver = LIB_MECHANIZE
        with browser:
            self.assertEquals(LIB_MECHANIZE, browser.get_driver().LIBRARY_NAME)

    def test_library_constants_with_zopeapp(self):
        browser = Browser()

        browser.default_driver = LIB_REQUESTS
        with browser(self.layer['app']):
            self.assertEquals(LIB_REQUESTS, browser.get_driver().LIBRARY_NAME)

        browser.default_driver = LIB_MECHANIZE
        with browser(self.layer['app']):
            self.assertEquals(LIB_MECHANIZE, browser.get_driver().LIBRARY_NAME)


class TestSwitchToRequestDriver(BrowserTestCase):
    layer = REQUESTS_TESTING

    @browsing
    def test_open_supports_choosing_library_when_doing_request(self, browser):
        browser.open(library=LIB_MECHANIZE)
        self.assertEquals('MechanizeDriver',
                          type(browser.get_driver()).__name__)

        browser.open(library=LIB_REQUESTS)
        self.assertEquals('RequestsDriver',
                          type(browser.get_driver()).__name__)

    @browsing
    def test_visit_supports_choosing_library_when_doing_request(self, browser):
        browser.visit(library=LIB_MECHANIZE)
        self.assertEquals('MechanizeDriver',
                          type(browser.get_driver()).__name__)

        browser.visit(library=LIB_REQUESTS)
        self.assertEquals('RequestsDriver',
                          type(browser.get_driver()).__name__)
