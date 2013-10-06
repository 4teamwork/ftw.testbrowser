from ftw.browser import browsing
from ftw.browser.pages import plone
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
