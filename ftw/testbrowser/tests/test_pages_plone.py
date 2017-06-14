from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID


@all_drivers
class TestPlonePageObject(BrowserTestCase):

    @browsing
    def test_not_logged_in(self, browser):
        browser.open(self.portal.portal_url())
        self.assertFalse(plone.logged_in())

    @browsing
    def test_logged_in(self, browser):
        browser.login().open(self.portal.portal_url())
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_view_on_root(self, browser):
        browser.open()
        self.assertEquals('listing_view', plone.view())

    @browsing
    def test_view_on_login_form(self, browser):
        browser.open(view='login_form')
        self.assertEquals('login_form', plone.view())


    @browsing
    def test_portal_type(self, browser):
        browser.open()
        self.assertEquals('plone-site', plone.portal_type())

    @browsing
    def test_view_and_portal_type(self, browser):
        browser.open()
        self.assertEquals(('listing_view', 'plone-site'),
                          plone.view_and_portal_type())

    @browsing
    def test_first_heading(self, browser):
        browser.open()
        self.assertEquals('Plone site', plone.first_heading())

    @browsing
    def test_first_heading_on_at_addform(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        self.assertEquals('Add Folder', plone.first_heading())

    @browsing
    def test_document_description(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='overview-controlpanel')
        self.assertEquals('Configuration area for Plone and add-on Products.',
                          plone.document_description())

    @browsing
    def test_no_document_description(self, browser):
        browser.open()
        self.assertEquals(None, plone.document_description())
