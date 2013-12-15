from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import OptionsNotFound
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestBrowserZ3CForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_sequence_widget_options(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        self.assertEquals(['paper bag', 'plastic bag'],
                          browser.find('Bag').options)

    @browsing
    def test_sequence_widget_option_map(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        self.assertEquals({'apple': 'Apple',
                           'banana': 'Banana',
                           'orange': 'Orange'},
                          browser.find('Fruits').option_map)

    @browsing
    def test_sequence_widget_inputs_by_value(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        self.assertEquals(['apple', 'banana', 'orange'],
                          sorted(browser.find('Fruits').inputs_by_value.keys()))

    @browsing
    def test_sequence_widget_inputs_by_label(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        self.assertEquals(['Apple', 'Banana', 'Orange'],
                          sorted(browser.find('Fruits').inputs_by_label.keys()))

    @browsing
    def test_fill_radio_fields(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Bag': 'plastic bag'})
        browser.find('Submit').click()
        self.assertEquals({u'bag': [u'plastic bag']}, browser.json)

    @browsing
    def test_fill_checkbox_fields(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Fruits': ['Banana', 'apple']})
        browser.find('Submit').click()
        self.assertEquals({u'fruits': [u'apple', u'banana']}, browser.json)

    @browsing
    def test_fill_checkbox_raises_when_value_not_available(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        with self.assertRaises(OptionsNotFound) as cm:
            browser.fill({'Fruits': ['Coconut']})
        self.assertEquals(
            'Could not find options [\'Coconut\'] for field "Fruits".',
            str(cm.exception))

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
