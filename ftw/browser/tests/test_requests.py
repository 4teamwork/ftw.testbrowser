from ftw.browser import browsing
from ftw.browser.pages import plone
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase


class TestBrowserRequests(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

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
