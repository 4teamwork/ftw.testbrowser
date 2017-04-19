from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.alldrivers import skip_driver
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD


@all_drivers
class TestCookies(FunctionalTestCase):

    @browsing
    def test_cookies(self, browser):
        browser.open(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()

        self.assertIn('__ac', browser.cookies)
        self.assertDictContainsSubset(
            {'expires': None,
             'path': '/'},
            browser.cookies['__ac'])


    @skip_driver(LIB_MECHANIZE, """
    The `webdav` method can only be used with a running ZServer.
    """)
    @browsing
    def test_webdav_cookies(self, browser):
        browser.open(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        browser.webdav('get')

        self.assertIn('__ac', browser.cookies)
        self.assertDictContainsSubset(
            {'expires': None,
             'path': '/'},
            browser.cookies['__ac'])
