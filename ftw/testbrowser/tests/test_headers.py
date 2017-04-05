from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.alldrivers import skip_driver


@all_drivers
class TestMechanizeHeaders(BrowserTestCase):

    @browsing
    def test_headers(self, browser):
        browser.open()
        # Plone 4: utf-8
        # Plone 5: UTF-8
        self.assertIn(browser.headers.get('content-type').lower(),
                      ('text/html; charset=utf-8',
                       'text/html;charset=utf-8'))

    @skip_driver(LIB_MECHANIZE, """
    The `webdav` method can only be used with a running ZServer.
    """)
    @browsing
    def test_webdav_headers(self, browser):
        browser.webdav('get')
        # Plone 4: text/html; charset=utf-8
        # Plone 5: text/html;charset=UTF-8
        self.assertEquals(
            'text/html;charset=utf-8',
            browser.headers.get('content-type').lower().replace(' ', ''))
