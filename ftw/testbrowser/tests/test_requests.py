from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from ftw.testbrowser.testing import BROWSER_ZSERVER_FUNCTIONAL_TESTING
from ftw.testbrowser.tests.helpers import register_view
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
from zope.publisher.browser import BrowserView


class TestMechanizeBrowserRequests(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

    @browsing
    def test_get_request(self, browser):
        browser.open('http://nohost/plone')
        self.assertEquals('http://nohost/plone', browser.url)

    @browsing
    def test_open_with_view_only(self, browser):
        browser.open(view='login_form')
        self.assertEquals('http://nohost/plone/login_form', browser.url)

    @browsing
    def test_open_site_root_by_default(self, browser):
        browser.open()
        self.assertEquals('http://nohost/plone', browser.url)

    @browsing
    def test_post_request(self, browser):
        browser.open('http://nohost/plone/login_form')
        self.assertFalse(plone.logged_in())

        browser.open('http://nohost/plone/login_form',
                     {'__ac_name': TEST_USER_NAME,
                      '__ac_password': TEST_USER_PASSWORD,
                      'form.submitted': 1})
        self.assertTrue(plone.logged_in())

    @browsing
    def test_post_request_with_umlauts(self, browser):
        browser.open(view='test-form-result', data={u'Uml\xe4ute': u'Uml\xe4ute'})
        self.assertEquals({u'Uml\xe4ute': u'Uml\xe4ute'}, browser.json)

    @browsing
    def test_exceptions_are_passed_to_test(self, browser):
        class FailingView(BrowserView):
            def __call__(self):
                raise ValueError('The value is wrong.')

        with register_view(FailingView, 'failing-view'):
            with self.assertRaises(ValueError) as cm:
                browser.open(view='failing-view')
            self.assertEquals(str(cm.exception), 'The value is wrong.')

    @browsing
    def test_visit_object(self, browser):
        folder = create(Builder('folder').titled('Test Folder'))
        browser.login().visit(folder)
        self.assertEquals('http://nohost/plone/test-folder', browser.url)

    @browsing
    def test_visit_view_on_object(self, browser):
        folder = create(Builder('folder').titled('Test Folder'))
        browser.login().visit(folder, view='folder_contents')
        self.assertEquals('http://nohost/plone/test-folder/folder_contents',
                          browser.url)

    @browsing
    def test_loading_string_html_without_request(self, browser):
        html = '\n'.join(('<html>',
                          '<h1>The heading</h1>',
                          '<html>'))

        browser.open_html(html)
        self.assertEquals('The heading', browser.css('h1').first.normalized_text())

    @browsing
    def test_loading_stream_html_without_request(self, browser):
        html = StringIO()
        html.write('<html>')
        html.write('<h1>The heading</h1>')
        html.write('<html>')

        browser.open_html(html)
        self.assertEquals('The heading', browser.css('h1').first.normalized_text())

    @browsing
    def test_open_html_sets_response_to_html_stream(self, browser):
        # When an exception happens within a test, the response content is dumped
        # to a temporary file for debugging purpose.
        # For having the HTML, which was set with open_html, in the temporary file
        # the response needs to contain this HTML and not html set previously or
        # nothing.

        html = '\n'.join(('<html>',
                          '<h1>The heading</h1>',
                          '<html>'))

        browser.open_html(html)
        browser.response.seek(0)
        self.assertEquals(html, browser.response.read())

    @browsing
    def test_logout_works(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        browser.login(hugo.getId()).open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        browser.logout().open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_relogin_works(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        browser.login(hugo.getId()).open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        john = create(Builder('user').named('John', 'Doe'))
        browser.login(john.getId()).open()
        self.assertEquals('Doe John', plone.logged_in())

    @browsing
    def test_login_with_member_object_works(self, browser):
        # Use the test user which has different ID and NAME,
        # but pass in the member object.
        mtool = getToolByName(self.layer['portal'], 'portal_membership')
        member = mtool.getMemberById(TEST_USER_ID)
        browser.login(member).open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_login_with_user_object_works(self, browser):
        # Use the test user which has different ID and NAME,
        # but pass in the user object.
        acl_users = getToolByName(self.layer['portal'], 'acl_users')
        user = acl_users.getUserById(TEST_USER_ID)
        browser.login(user).open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_append_request_header(self, browser):
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((TEST_USER_NAME, TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.open()  # reload
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_replace_request_header(self, browser):
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        john = create(Builder('user').named('John', 'Doe'))

        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((hugo.getId(), TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        browser.replace_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((john.getId(), TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals('Doe John', plone.logged_in())

    @browsing
    def test_clear_request_header_with_header_selection(self, browser):
        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((TEST_USER_NAME, TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.clear_request_header('Authorization')
        browser.open()
        self.assertFalse(plone.logged_in())


class TestRequestslibBrowserRequests(TestCase):

    layer = BROWSER_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_open_supports_choosing_library_when_doing_request(self, browser):
        browser.open(library=LIB_MECHANIZE)
        self.assertEquals('mechanize',
                          browser.response.__class__.__module__.split('.')[0])

        browser.open(library=LIB_REQUESTS)
        self.assertEquals('requests',
                          browser.response.__class__.__module__.split('.')[0])

    @browsing
    def test_visit_supports_choosing_library_when_doing_request(self, browser):
        browser.visit(library=LIB_MECHANIZE)
        self.assertEquals('mechanize',
                          browser.response.__class__.__module__.split('.')[0])

        browser.visit(library=LIB_REQUESTS)
        self.assertEquals('requests',
                          browser.response.__class__.__module__.split('.')[0])

    @browsing
    def test_url_with_requests_libr(self, browser):
        browser.open(library=LIB_REQUESTS)
        self.assertEquals(self.layer['portal'].absolute_url(),
                          browser.url)

    def test_no_browser_setup_uses_requests_library(self):
        with Browser() as browser:
            browser.open(self.layer['portal'].absolute_url())
            self.assertEquals('requests',
                              browser.response.__class__.__module__.split('.')[0])

    def test_form_submitting_with_requests_library(self):
        with Browser() as browser:
            browser.visit(view='test-form')
            browser.css('#test-form').first.submit()
            self.assertEquals({'textfield': '',
                               'submit-button': 'Submit'}, browser.json)

    @browsing
    def test_append_request_header(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((TEST_USER_NAME, TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.open()  # reload
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_replace_request_header(self, browser):
        browser.request_library = LIB_REQUESTS
        hugo = create(Builder('user').named('Hugo', 'Boss'))
        john = create(Builder('user').named('John', 'Doe'))

        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((hugo.getId(), TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals('Boss Hugo', plone.logged_in())

        browser.replace_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((john.getId(), TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals('Doe John', plone.logged_in())

    @browsing
    def test_clear_request_header_with_header_selection(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.append_request_header('Authorization', 'Basic {0}'.format(
                ':'.join((TEST_USER_NAME, TEST_USER_PASSWORD)).encode('base64')))
        browser.open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.clear_request_header('Authorization')
        browser.open()
        self.assertFalse(plone.logged_in())

    @browsing
    def test_login_and_logout(self, browser):
        browser.request_library = LIB_REQUESTS
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.login().open()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.logout().open()
        self.assertFalse(plone.logged_in())
