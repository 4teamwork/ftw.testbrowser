from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestBrowserZ3CForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_sequence_widget_options(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        self.assertEquals(['plastic bag', 'paper bag'],
                          browser.find('Bag').options)

    @browsing
    def test_fill_radio_fields(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Bag': 'plastic bag'})
        browser.find('Submit').click()
        self.assertEquals({u'bag': [u'plastic bag']}, browser.json)

    @browsing
    def test_fill_checkbox_fields(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Fruits': ['Banana', 'Apple']})
        browser.find('Submit').click()
        self.assertEquals({u'fruits': [u'Apple', u'Banana']}, browser.json)

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

    @browsing
    def test_datefield_form_fill(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Delivery date': datetime(2010, 12, 22, 10, 30, 00)})
        browser.find('Submit').click()
        self.assertEquals({u'delivery_date': u'2010-12-22T10:30:00'}, browser.json)
