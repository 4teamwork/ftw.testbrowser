from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import z3cform
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestZ3cformPageObject(BrowserTestCase):

    @browsing
    def test_erroneous_fields_default_form(self, browser):
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Folder')
        browser.find('Save').click()

        self.assertEquals(browser.previous_url, browser.url)

        self.assertEquals({u'Title': ['Required input is missing.']},
                          z3cform.erroneous_fields())

    @browsing
    def test_erroneous_fields_missing_default_form(self, browser):
        browser.visit(view='test-form')
        with self.assertRaises(ValueError) as cm:
            z3cform.erroneous_fields()

        self.assertEqual(
            "Could not find the default `#form` on the current page, please "
            "provide a valid form. Available forms are: "
            "['test-form', 'searchGadget_form', 'test-get-form']",
            cm.exception.message)

    @browsing
    def test_erroneous_fields_with_custom_form(self, browser):
        browser.visit(view='test-form')
        self.assertEqual(
            {}, z3cform.erroneous_fields(browser.forms['test-form']))
