from ftw.testbrowser import Browser
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.tests import FunctionalTestCase


class TestDefaultDriver(FunctionalTestCase):

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
