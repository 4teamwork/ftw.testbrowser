from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import OnlyOneValueAllowed
from ftw.testbrowser.exceptions import OptionsNotFound
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME


@all_drivers
class TestSequenceWidget(BrowserTestCase):

    @browsing
    def test_sequence_widget_options(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        self.assertEquals(['paper bag', 'plastic bag'],
                          browser.find('Bag').options)

    @browsing
    def test_sequence_widget_option_map(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        self.assertEquals({'apple': 'Apple',
                           'banana': 'Banana',
                           'orange': 'Orange'},
                          browser.find('Fruits').option_map)

    @browsing
    def test_sequence_widget_inputs_by_value(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        self.assertEquals(['apple', 'banana', 'orange'],
                          sorted(browser.find('Fruits').inputs_by_value.keys()))

    @browsing
    def test_sequence_widget_inputs_by_label(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        self.assertEquals(['Apple', 'Banana', 'Orange'],
                          sorted(browser.find('Fruits').inputs_by_label.keys()))

    @browsing
    def test_radio_widget_has_multiple_False(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        self.assertFalse(browser.find('Bag').multiple,
                         'The radio field "Bag" should only allow one option.')

    @browsing
    def test_fill_radio_fields(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Bag': 'plastic bag'})
        browser.find('Submit').click()
        self.assertEquals({u'bag': [u'plastic bag']}, browser.json)

    @browsing
    def test_fill_radio_multiple_options_raises_exception(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        with self.assertRaises(OnlyOneValueAllowed):
            browser.fill({'Bag': ['plastic bag', 'paper bag']})

    @browsing
    def test_checkbox_widget_has_multiple_True(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        self.assertTrue(browser.find('Fruits').multiple,
                        'The radio field "Fruits" should allow multiple options.')

    @browsing
    def test_fill_checkbox_fields(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Fruits': ['Banana', 'apple']})
        browser.find('Submit').click()
        self.assertEquals({u'fruits': [u'apple', u'banana']}, browser.json)

    @browsing
    def test_fill_checkbox_raises_when_value_not_available(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        with self.assertRaises(OptionsNotFound) as cm:
            browser.fill({'Fruits': ['Coconut']})
        self.assertEquals(
            'Could not find options [\'Coconut\'] for field "Fruits".'
            ' Options: "Apple", "Banana", "Orange"',
            str(cm.exception))
