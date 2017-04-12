from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD


@all_drivers
class TestBrowserSession(FunctionalTestCase):

    @browsing
    def test_browser_stays_logged_in(self, browser):
        browser.open()
        self.assertFalse(plone.logged_in())

        browser.visit(view='login_form')
        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

        browser.visit(view='/')
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_previous_url_is_None_on_first_page(self, browser):
        self.assertEquals(None, browser.previous_url)
        browser.open()
        self.assertEquals(None, browser.previous_url)

    @browsing
    def test_previous_url_is_set_on_link_click(self, browser):
        browser.open()
        browser.find('Log in').click()
        self.assertEquals(self.portal.portal_url(), browser.previous_url)
