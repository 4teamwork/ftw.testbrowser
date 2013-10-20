from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.form import Form
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase


class TestBrowserForms(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

    @browsing
    def test_find_form_by_field_label(self, browser):
        browser.open(view='login_form')
        self.assertEquals(Form, type(Form.find_form_by_labels_or_names('Login Name')))

    @browsing
    def test_exception_when_field_not_found(self, browser):
        browser.open(view='login_form')
        with self.assertRaises(FormFieldNotFound) as cm:
            Form.find_form_by_labels_or_names('First Name')
        self.assertEquals('Could not find form field: "First Name"',
                          str(cm.exception))

    @browsing
    def test_exception_when_chaning_fields_in_different_forms(self, browser):
        browser.open(view='login_form')
        with self.assertRaises(AmbiguousFormFields):
            Form.find_form_by_labels_or_names('Login Name', 'Search Site')

    @browsing
    def test_fill_field_by_name(self, browser):
        browser.open(view='login_form')
        self.assertEquals(u'', browser.forms['login_form'].values['__ac_name'])

        browser.fill({'__ac_name': 'hugo.boss'})
        self.assertEquals(u'hugo.boss', browser.forms['login_form'].values['__ac_name'])

    @browsing
    def test_fill_field_by_label(self, browser):
        browser.open(view='login_form')
        self.assertEquals(u'', browser.forms['login_form'].values['__ac_name'])

        browser.fill({'Login Name': 'hugo.boss'})
        self.assertEquals(u'hugo.boss', browser.forms['login_form'].values['__ac_name'])

    @browsing
    def test_submit_form(self, browser):
        browser.open(view='login_form')
        self.assertFalse(plone.logged_in())

        browser.fill({'Login Name': TEST_USER_NAME,
                      'Password': TEST_USER_PASSWORD}).submit()
        self.assertEquals(TEST_USER_ID, plone.logged_in())

    @browsing
    def test_fill_archetypes_field(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': 'The Folder'}).submit()
        self.assertEquals('folder_listing', plone.view())
        self.assertEquals('The Folder', plone.first_heading())

    @browsing
    def test_fill_archtypes_field_with_description(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': 'The Folder',
                      'Description': 'The folder description'}).submit()
        self.assertEquals('folder_listing', plone.view())



class TestSubmittingForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_submitting_form_should_not_contain_button_values(self, browser):
        browser.visit(view='test-form')
        browser.css('#test-form').first.submit()
        self.assertEquals({'textfield': ''}, browser.json)

    @browsing
    def test_clicking_submit_contains_button_name_in_request(self, browser):
        browser.visit(view='test-form')
        browser.find('Submit').click()
        self.assertEquals({'textfield': '',
                           'submit-button': 'Submit'}, browser.json)

    @browsing
    def test_clicking_cancel_contains_button_name_in_request(self, browser):
        browser.visit(view='test-form')
        browser.find('Cancel').click()
        self.assertEquals({'textfield': '',
                           'cancel-button': 'Cancel'}, browser.json)
