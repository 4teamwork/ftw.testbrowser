from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase


class TestBrowserSession(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

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
