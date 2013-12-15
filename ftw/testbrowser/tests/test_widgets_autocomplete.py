from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestBrowserZ3CForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_autocomplete_form_fill(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Payment': 'mastercard'})
        browser.find('Submit').click()
        self.assertEquals({u'payment': [u'mastercard']}, browser.json)

    @browsing
    def test_autocomplete_query(self, browser):
        browser.login().visit(view='test-z3cform-shopping')

        self.assertEquals([['cash', 'Cash'],
                           ['mastercard', 'MasterCard']],
                          browser.find('Payment').query('ca'))
