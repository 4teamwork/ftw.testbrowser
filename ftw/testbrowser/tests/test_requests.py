from StringIO import StringIO
from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from ftw.testbrowser.tests.helpers import register_view
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase
from zope.publisher.browser import BrowserView


class TestBrowserRequests(TestCase):

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
