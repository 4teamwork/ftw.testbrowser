from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase
from urlparse import urljoin


class TestBrowserZ3CForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_autocomplete_form_fill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Payment': 'mastercard'})
        browser.find('Submit').click()
        self.assertEquals({u'payment': [u'mastercard']}, browser.json)

    @browsing
    def test_autocomplete_query(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')

        self.assertEquals([['cash', 'Cash'],
                           ['mastercard', 'MasterCard']],
                          browser.find('Payment').query('ca'))

    @browsing
    def test_autocomplete_query_with_querystring_in_base_url(self, browser):
        view_url = browser._normalize_url(None, view='test-z3cform-shopping')
        url = urljoin(view_url, '?key=value')
        browser.login(SITE_OWNER_NAME).visit(url)

        self.assertEquals([['cash', 'Cash'],
                           ['mastercard', 'MasterCard']],
                          browser.find('Payment').query('ca'))
