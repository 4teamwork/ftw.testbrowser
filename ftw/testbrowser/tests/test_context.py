from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import ContextNotFound
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME


@all_drivers
class TestBrowserContext(BrowserTestCase):

    def setUp(self):
        super(TestBrowserContext, self).setUp()
        self.grant('Manager')

    @browsing
    def test_context_can_be_retrieved_from_current_folder(self, browser):
        folder = create(Builder('folder').titled(u'The Folder'))
        browser.login().visit(folder)
        self.assertEquals(folder, browser.context)

    @browsing
    def test_context_when_on_a_view(self, browser):
        folder = create(Builder('folder').titled(u'The Folder'))
        browser.login().visit(folder, view='folder_contents')
        self.assertEquals(folder, browser.context)

    @browsing
    def test_context_when_url_contains_view(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')

        browser.fill({'Title': u'Page',
                      'Exclude from navigation': True}).save()
        statusmessages.assert_no_error_messages()
        self.sync_transaction()

        self.assertEquals(self.portal.get('page'), browser.context)

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
