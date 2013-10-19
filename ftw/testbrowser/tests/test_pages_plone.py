from ftw.testbrowser import browsing
from ftw.testbrowser.pages import plone
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase


class TestPlonePageObject(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

    @browsing
    def test_not_logged_in(self, browser):
        browser.open('http://nohost/plone')
        self.assertFalse(plone.logged_in())

    @browsing
    def test_logged_in(self, browser):
        browser.login().open('http://nohost/plone')
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_view_on_root(self, browser):
        browser.open()
        self.assertEquals('folder_listing', plone.view())

    @browsing
    def test_view_on_login_form(self, browser):
        browser.open(view='login_form')
        self.assertEquals('login_form', plone.view())
