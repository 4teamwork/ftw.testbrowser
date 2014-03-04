from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import ContextNotFound
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase


class TestBrowserContext(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        login(self.layer['portal'], TEST_USER_NAME)

    @browsing
    def test_context_can_be_retrieved_from_current_folder(self, browser):
        folder = create(Builder('folder').titled('The Folder'))
        browser.login().visit(folder)
        self.assertEquals(folder, browser.context)

    @browsing
    def test_context_when_on_a_view(self, browser):
        folder = create(Builder('folder').titled('The Folder'))
        browser.login().visit(folder, view='folder_contents')
        self.assertEquals(folder, browser.context)

    @browsing
    def test_execption_when_not_viewing_any_page(self, browser):
        with self.assertRaises(ContextNotFound) as cm:
            browser.context

        self.assertEquals('Not viewing any page.',
                          str(cm.exception))

    @browsing
    def test_exception_when_page_has_no_context_information(self, browser):
        html = '\n'.join(('<html>',
                          '<h1>The heading</h1>',
                          '</html>'))
        browser.open_html(html)

        with self.assertRaises(ContextNotFound) as cm:
            browser.context

        self.assertEquals('No <base> tag found on current page.',
                          str(cm.exception))

    @browsing
    def test_path_has_to_be_within_current_plone_site(self, browser):
        html = '\n'.join(('<html>',
                          '<base href="http://localhost/foo/bar" />'
                          '</html>'))
        browser.open_html(html)

        with self.assertRaises(ContextNotFound) as cm:
            browser.context

        self.assertEquals(
            'Expected URL path to start with the Plone site'
            ' path "/plone" but it is "/foo/bar"',
            str(cm.exception))
