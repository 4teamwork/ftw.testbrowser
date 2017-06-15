from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser import HTTPClientError
from ftw.testbrowser import HTTPServerError
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.pages import plone
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import capture_streams
from ftw.testbrowser.tests.helpers import register_view
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from StringIO import StringIO
from zExceptions import BadRequest
from zope.globalrequest import getRequest
from zope.publisher.browser import BrowserView


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


@all_drivers
class TestBrowserCore(BrowserTestCase):

    @browsing
    def test_contents(self, browser):
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
    def test_headers(self, browser):
        browser.open()
        self.assertDictContainsSubset({'content-language': 'en'}, browser.headers)

    @browsing
    def test_headers_with_open_html(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assertEquals({}, browser.headers)

    @browsing
    def test_cookies(self, browser):
        browser.open(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertDictContainsSubset(AC_COOKIE_INFO,
                                      browser.cookies.get('__ac', None))

    @browsing
    def test_url(self, browser):
        browser.open(view='login_form')
        self.assertEquals('/'.join((self.layer['portal'].absolute_url(),
                                    'login_form')),
                          browser.url)

    @browsing
    def test_status_is_exposed(self, browser):
        browser.open()
        self.assertEquals(200, browser.status_code)
        self.assertEquals('OK', browser.status_reason.upper())

    @browsing
    def test_raises_404_as_client_error(self, browser):
        with self.assertRaises(HTTPClientError) as cm:
            browser.open(view='missing')

        self.assertEquals(404, cm.exception.status_code)
        self.assertEquals('Not Found', cm.exception.status_reason)
        self.assertEquals('404 Not Found', str(cm.exception))

        with self.assertRaises(HTTPClientError):
            browser.reload()

        browser.raise_http_errors = False
        browser.reload()

    @browsing
    def test_raises_500_as_server_error(self, browser):
        class ViewWithError(BrowserView):
            def __call__(self):
                raise ValueError('The value is wrong.')

        with register_view(ViewWithError, 'view-with-error'):
            with capture_streams(stderr=StringIO()):
                with self.assertRaises(HTTPServerError) as cm:
                    browser.open(view='view-with-error')

            self.assertEquals(500, cm.exception.status_code)
            self.assertEquals('Internal Server Error', cm.exception.status_reason)

            with capture_streams(stderr=StringIO()):
                with self.assertRaises(HTTPServerError):
                    browser.reload()

            browser.raise_http_errors = False
            with capture_streams(stderr=StringIO()):
                browser.reload()

    @browsing
    def test_expect_http_error(self, browser):
        class GetRecordById(BrowserView):
            def __call__(self):
                raise BadRequest('Missing "id" parameter.')

        with register_view(GetRecordById, 'get-record-by-id'):
            with browser.expect_http_error():
                browser.open(view='get-record-by-id')

    @browsing
    def test_expect_http_error_raises_when_no_error_happens(self, browser):
        with self.assertRaises(AssertionError) as cm:
            with browser.expect_http_error():
                browser.open()

        self.assertEquals('Expected a HTTP error but it didn\'t occur.',
                          str(cm.exception))

    @browsing
    def test_expect_http_error_and_assert_correct_status_code(self, browser):
        with browser.expect_http_error(code=404):
            browser.open(view='no-such-view')

    @browsing
    def test_expect_http_error_and_assert_incorrect_status_code(self, browser):
        with self.assertRaises(AssertionError) as cm:
            with browser.expect_http_error(code=400):
                browser.open(view='no-such-view')

        self.assertEquals('Expected HTTP error with status code 400, got 404.',
                          str(cm.exception))

    @browsing
    def test_expect_http_error_and_assert_correct_status_reason(self, browser):
        with browser.expect_http_error(reason='Not Found'):
            browser.open(view='no-such-view')

    @browsing
    def test_expect_http_error_and_assert_incorrect_status_reason(self, browser):
        with self.assertRaises(AssertionError) as cm:
            with browser.expect_http_error(reason='Bad Request'):
                browser.open(view='no-such-view')

        self.assertEquals(
            'Expected HTTP error with status \'Bad Request\', got \'Not Found\'.',
            str(cm.exception))

    @browsing
    def test_expect_unauthorized_successful_when_anonymous(self, browser):
        with browser.expect_unauthorized():
            browser.open(view='plone_control_panel')

    @browsing
    def test_expect_unauthorized_failing_when_anonymous(self, browser):
        with self.assertRaises(AssertionError) as cm:
            with browser.expect_unauthorized():
                browser.open()

        self.assertIn(str(cm.exception), [
            # Requests (OK)
            'Expected request to be unauthorized, but got: 200 OK at {}'.format(
                self.portal.absolute_url()),
            # Mechanize (Ok)
            'Expected request to be unauthorized, but got: 200 Ok at {}'.format(
                self.portal.absolute_url())])

    @browsing
    def test_expect_unauthorized_successful_when_logged_in(self, browser):
        browser.login()
        with browser.expect_unauthorized():
            browser.open(view='plone_control_panel')

    @browsing
    def test_expect_unauthorized_failing_when_logged_in(self, browser):
        with self.assertRaises(AssertionError) as cm:
            browser.login()
            with browser.expect_unauthorized():
                browser.open()

        self.assertIn(str(cm.exception), [
            # Requests (OK)
            'Expected request to be unauthorized, but got: 200 OK at {}'.format(
                self.portal.absolute_url()),
            # Mechanize (Ok)
            'Expected request to be unauthorized, but got: 200 Ok at {}'.format(
                self.portal.absolute_url())])

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
    def test_base_url_is_None_when_unkown(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assertIsNone(browser.base_url)

    @browsing
    def test_url_is_None_with_open_html(self, browser):
        browser.open_html('<html><head></head></html>')
        self.assertIsNone(browser.url)

    @browsing
    def test_cloning_copies_cookies(self, browser):
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
    def test_cloning_a_browser_copies_headers(self, browser):
        browser.login().open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        with browser.clone() as subbrowser:
            subbrowser.open()
            self.assertEquals(TEST_USER_ID, plone.logged_in(subbrowser))
            subbrowser.login(SITE_OWNER_NAME).reload()
            self.assertEquals(SITE_OWNER_NAME, plone.logged_in(subbrowser))

    @browsing
    def test_opening_preserves_global_request(self, browser):
        browser.open()
        self.assertIsNotNone(getRequest())

    def assert_starts_with(self, start, contents):
        self.assertTrue(
            contents.startswith(start),
            'Expected browser.contents to start with "{0}",'
            ' but it is starting with "{1}"'.format(
                start, contents[:len(start)]))
