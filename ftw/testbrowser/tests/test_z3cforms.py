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
        browser.fill({'Bag': 'plastic bag'}).submit()
        self.assertEquals({u'bag': [u'plastic bag']}, browser.json)

    @browsing
    def test_fill_checkbox_fields(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Fruits': ['Banana', 'Apple']}).submit()
        self.assertEquals({u'fruits': [u'Apple', u'Banana']}, browser.json)
