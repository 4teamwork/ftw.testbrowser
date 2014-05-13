from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.testing import BROWSER_ZSERVER_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase


AC_COOKIE_INFO = {'comment': None,
                  'domain': 'localhost.local',
                  'name': '__ac',
                  'domain_initial_dot': False,
                  'expires': None,
                  # 'value': ...,  The value changes.
                  'domain_specified': False,
                  '_rest': {'HTTPOnly': None},
                  'version': 0,
                  'port_specified': False,
                  'rfc2109': False,
                  'discard': True,
                  'path_specified': True,
                  'path': '/',
                  'port': None,
                  'comment_url': None,
                  'secure': False}


class TestBrowserCore(TestCase):

    layer = BROWSER_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_contents_MECHANIZE(self, browser):
        browser.open()
        self.assert_starts_with('<!DOCTYPE html>', browser.contents.strip())

    @browsing
    def test_contents_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open()
        self.assert_starts_with('<!DOCTYPE html>', browser.contents.strip())

    @browsing
    def test_contents_with_open_html(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assert_starts_with('<html>', browser.contents.strip())

    def test_contents_verifies_setup(self):
        with self.assertRaises(BrowserNotSetUpException):
            Browser().contents

    @browsing
    def test_json(self, browser):
        browser.open_html('{"foo": "bar"}')
        self.assertEquals({'foo': 'bar'}, browser.json)

    @browsing
    def test_json_raises_when_parsing_not_possible(self, browser):
        browser.open_html('not json')
        with self.assertRaises(ValueError) as cm:
            browser.json
        self.assertEquals('No JSON object could be decoded', str(cm.exception))

    @browsing
    def test_headers_MECHANIZE(self, browser):
        browser.open()
        self.assertDictContainsSubset({'content-language': 'en'}, browser.headers)

    @browsing
    def test_headers_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open()
        self.assertDictContainsSubset({'content-language': 'en'}, browser.headers)

    @browsing
    def test_headers_with_open_html(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assertEquals({}, browser.headers)

    @browsing
    def test_cookies_MECHANIZE(self, browser):
        browser.open(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertDictContainsSubset(AC_COOKIE_INFO,
                                      browser.cookies.get('__ac', None))

    @browsing
    def test_url_MECHANIZE(self, browser):
        browser.open(view='login_form')
        self.assertEquals('/'.join((self.layer['portal'].absolute_url(),
                                    'login_form')),
                          browser.url)

    @browsing
    def test_url_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open(view='login_form')
        self.assertEquals('/'.join((self.layer['portal'].absolute_url(),
                                    'login_form')),
                          browser.url)

    @browsing
    def test_url_is_None_with_open_html(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assertIsNone(browser.url)

    def assert_starts_with(self, start, contents):
        self.assertTrue(
            contents.startswith(start),
            'Expected browser.contents to start with "{0}",'
            ' but it is starting with "{1}"'.format(
                start, contents[:len(start)]))
