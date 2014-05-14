from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from ftw.testbrowser.testing import BROWSER_ZSERVER_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase


class TestMechanizeCookies(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

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


class TestZServerHeaders(TestCase):

    layer = BROWSER_ZSERVER_FUNCTIONAL_TESTING

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

    @browsing
    def test_webdav_cookies(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        browser.webdav('get')

        self.assertIn('__ac', browser.cookies)
        self.assertDictContainsSubset(
            {'expires': None,
             'path': '/'},
            browser.cookies['__ac'])
