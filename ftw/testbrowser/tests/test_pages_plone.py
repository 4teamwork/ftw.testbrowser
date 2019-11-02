from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import nondefault_browsing
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID


@all_drivers
class TestPlonePageObject(BrowserTestCase):

    @nondefault_browsing
    def test_not_logged_in(self, browser):
        browser.open(self.portal.portal_url())
        self.assertFalse(plone.logged_in(browser=browser))

    @nondefault_browsing
    def test_logged_in(self, browser):
        browser.login().open(self.portal.portal_url())
        self.assertEqual(TEST_USER_ID, plone.logged_in(browser=browser))

    @nondefault_browsing
    def test_view_on_root(self, browser):
        browser.open()
        self.assertEqual('listing_view', plone.view(browser=browser))

    @nondefault_browsing
    def test_view_on_login_form(self, browser):
        browser.open(view='login_form')
        self.assertEqual('login_form', plone.view(browser=browser))

    @nondefault_browsing
    def test_portal_type(self, browser):
        browser.open()
        self.assertEqual('plone-site', plone.portal_type(browser=browser))

    @nondefault_browsing
    def test_view_and_portal_type(self, browser):
        browser.open()
        self.assertEqual(('listing_view', 'plone-site'),
                         plone.view_and_portal_type(browser=browser))

    @nondefault_browsing
    def test_first_heading(self, browser):
        browser.open()
        self.assertEqual('Plone site', plone.first_heading(browser=browser))

    @nondefault_browsing
    def test_first_heading_on_at_addform(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder', browser=browser)
        self.assertEqual('Add Folder', plone.first_heading(browser=browser))

    @nondefault_browsing
    def test_document_description(self, browser):
        browser.login(SITE_OWNER_NAME).open(view='overview-controlpanel')
        self.assertEqual('Configuration area for Plone and add-on Products.',
                         plone.document_description(browser=browser))

    @nondefault_browsing
    def test_no_document_description(self, browser):
        browser.open()
        self.assertEqual(None, plone.document_description(browser=browser))
