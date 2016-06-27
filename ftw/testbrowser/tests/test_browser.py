from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_ZSERVER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase
from zExceptions import NotFound
from zope.globalrequest import getRequest


AC_COOKIE_INFO = {'comment': None,
                  # 'domain': ... may be 'localhost.local' or '0.0.0.0'
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
    def test_contents_raises_when_on_blank_page(self, browser):
        with self.assertRaises(BlankPage) as cm:
            browser.contents
        self.assertEquals('The browser is on a blank page.', str(cm.exception))

    @browsing
    def test_json(self, browser):
        browser.open_html('{"foo": "bar"}')
        self.assertEquals({'foo': 'bar'}, browser.json)

    @browsing
    def test_json_raises_when_on_blank_page(self, browser):
        with self.assertRaises(BlankPage) as cm:
            browser.json
        self.assertEquals('The browser is on a blank page.', str(cm.exception))

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
    def test_cookies_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
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
    def test_url_is_None_when_previous_request_had_exception(self, browser):
        browser.open()
        with self.assertRaises(NotFound):
            browser.open(view='this/path/does/not/exist')
        self.assertIsNone(browser.url)

    @browsing
    def test_base_url_is_base_url_tag(self, browser):
        portal_url = self.layer['portal'].absolute_url() + '/'
        folder_contents_url = portal_url + 'folder_contents'

        browser.login(SITE_OWNER_NAME).open(folder_contents_url)
        self.assertEquals(portal_url, browser.base_url)
        self.assertEquals(folder_contents_url, browser.url)

    @browsing
    def test_base_url_falls_back_to_page_url(self, browser):
        portal_url = self.layer['portal'].absolute_url() + '/'
        # The test-form-result returns json and thus has no base tag
        view_url = portal_url + 'test-form-result'

        browser.login(SITE_OWNER_NAME).open(view_url)
        self.assertEquals(view_url, browser.base_url)

    @browsing
    def test_base_url_with_open_html(self, browser):
        browser.open_html('<html><head>'
                          '<base href="http://nohost/foo/bar" />'
                          '</head></html>')
        self.assertEquals('http://nohost/foo/bar', browser.base_url)

    @browsing
    def test_base_url_is_None_when_unkown(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assertIsNone(browser.base_url)

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

    @browsing
    def test_cloning_copies_cookies_MECHBROWSER(self, browser):
        browser.open(view='login_form').fill(
            {'Login Name': TEST_USER_NAME,
             'Password': TEST_USER_PASSWORD}).submit()
        self.assertTrue(browser.css('#user-name'))

        with browser.clone() as subbrowser:
            subbrowser.open()
            self.assertTrue(subbrowser.css('#user-name'))
            subbrowser.find('Log out').click()
            self.assertFalse(subbrowser.css('#user-name'))

        browser.reload()
        self.assertTrue(browser.css('#user-name'))

    @browsing
    def test_cloning_copies_cookies_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open(view='login_form').fill(
            {'Login Name': TEST_USER_NAME,
             'Password': TEST_USER_PASSWORD}).submit()
        self.assertTrue(browser.css('#user-name'))

        with browser.clone() as subbrowser:
            subbrowser.open()
            self.assertTrue(subbrowser.css('#user-name'))
            subbrowser.find('Log out').click()
            self.assertFalse(subbrowser.css('#user-name'))

        browser.reload()
        self.assertTrue(browser.css('#user-name'))

    @browsing
    def test_cloning_a_browser_copies_headers_MECHBROWSER(self, browser):
        browser.login().open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        with browser.clone() as subbrowser:
            subbrowser.open()
            self.assertEquals(TEST_USER_ID, plone.logged_in(subbrowser))
            subbrowser.login(SITE_OWNER_NAME).reload()
            self.assertEquals(SITE_OWNER_NAME, plone.logged_in(subbrowser))

    @browsing
    def test_cloning_a_browser_copies_headers_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.login().open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        with browser.clone() as subbrowser:
            subbrowser.open()
            self.assertEquals(TEST_USER_ID, plone.logged_in(subbrowser))
            subbrowser.login(SITE_OWNER_NAME).reload()
            self.assertEquals(SITE_OWNER_NAME, plone.logged_in(subbrowser))

        browser.reload()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_opening_preserves_global_request_MECHANIZE(self, browser):
        browser.open()
        self.assertIsNotNone(getRequest())

    @browsing
    def test_opening_preserves_global_request_REQUESTS(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open()
        self.assertIsNotNone(getRequest())

    def assert_starts_with(self, start, contents):
        self.assertTrue(
            contents.startswith(start),
            'Expected browser.contents to start with "{0}",'
            ' but it is starting with "{1}"'.format(
                start, contents[:len(start)]))
