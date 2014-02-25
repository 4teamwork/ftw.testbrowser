from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.form import Form
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from ftw.testbrowser.widgets.base import PloneWidget
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from unittest2 import TestCase
import lxml.html


class TestBrowserForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_find_form_by_field_label(self, browser):
        browser.open(view='login_form')
        self.assertEquals(Form, type(Form.find_form_by_labels_or_names('Login Name')))

    @browsing
    def test_exception_when_field_not_found(self, browser):
        browser.open(view='login_form')
        with self.assertRaises(FormFieldNotFound) as cm:
            Form.find_form_by_labels_or_names('First Name')
        self.assertTrue(
            str(cm.exception).startswith('Could not find form field: "First Name".'
                                         ' Fields: '),
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
    def test_forms_are_not_wrapped_multiple_times(self, browser):
        browser.open(view='login_form')
        form = browser.forms['login_form']
        self.assertEquals(Form, type(form))
        self.assertEquals(lxml.html.FormElement, type(form.node))

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
    def test_fill_archtypes_field_with_unicode_umlauts(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': u'F\xf6lder',
                      'Description': u'The f\xf6lder description'}).submit()
        self.assertEquals('folder_listing', plone.view())
        self.assertEquals(u'F\xf6lder', plone.first_heading())

    @browsing
    def test_fill_archtypes_field_with_utf8_umlauts(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': u'F\xf6lder'.encode('utf-8'),
                      'Description': u'The f\xf6lder description'.encode('utf-8')}).submit()
        self.assertEquals('folder_listing', plone.view())
        self.assertEquals(u'F\xf6lder', plone.first_heading())

    @browsing
    def test_fill_checkbox_field(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        self.assertEquals(False, browser.find('Exclude from navigation').checked)
        browser.fill({'Exclude from navigation': True})
        self.assertEquals(True, browser.find('Exclude from navigation').checked)

    @browsing
    def test_filling_checkbox_without_a_value(self, browser):
        # Having checkboxes without a value attribtue is invalid but common.
        # The common default is to use "on" as the value.
        browser.visit(view='test-form')
        browser.fill({'checkbox-without-value': True}).submit()
        self.assertDictContainsSubset(
            {u'checkbox-without-value': u'on'},
            browser.json)

    @browsing
    def test_at_fill_tinymce_field(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': 'The page',
                      'Body Text': '<p>The body text.</p>'}).submit()
        self.assertEquals('The body text.',
                          browser.css('#content-core').first.normalized_text())

    @browsing
    def test_at_save_add_form(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': 'The page'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals('http://nohost/plone/the-page', browser.url)

    @browsing
    def test_find_submit_buttons(self, browser):
        browser.open(view='login_form')
        form = Form(Form.find_form_element_by_label_or_name('Login Name'))
        button = form.find_submit_buttons().first
        self.assertEquals('Log in', button.value)

    @browsing
    def test_find_widget_in_form(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        form = Form.find_form_by_labels_or_names('Title')
        widget = Form.find_widget_in_form(form, 'Title')
        self.assertEquals('div', widget.tag)
        self.assertEquals(PloneWidget, type(widget))


class TestSubmittingForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_should_send_default_submit_button_value(self, browser):
        browser.visit(view='test-form')
        browser.css('#test-form').first.submit()
        self.assertEquals({'textfield': '',
                           'submit-button': 'Submit'}, browser.json)

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


class TestSelectField(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

    @browsing
    def test_select_value(self, browser):
        browser.open_html('\n'.join((
                    '<html><body>',
                    ' <form id="form">',
                    '  <label for="field">Select Field</label>',
                    '  <select id="field" name="field">',
                    '    <option value="foo" selected>Foo</option>',
                    '    <option value="bar">Bar</option>',
                    '    <option value="baz">Baz</option>',
                    '  </select>',
                    ' </form>'
                    '</body></html>')))

        self.assertEquals('foo', browser.find('Select Field').value)
        browser.find('Select Field').value = 'bar'
        self.assertEquals('bar', browser.find('Select Field').value)

    @browsing
    def test_fill_value(self, browser):
        browser.open_html('\n'.join((
                    '<html><body>',
                    ' <form id="form">',
                    '  <label for="field">Select Field</label>',
                    '  <select id="field" name="field">',
                    '    <option value="foo" selected>Foo</option>',
                    '    <option value="bar">Bar</option>',
                    '    <option value="baz">Baz</option>',
                    '  </select>',
                    ' </form>'
                    '</body></html>')))

        self.assertEquals('foo', browser.find('Select Field').value)
        browser.fill({'Select Field': 'bar'})
        self.assertEquals('bar', browser.find('Select Field').value)

    @browsing
    def test_fill_multi_select(self, browser):
        browser.open_html('\n'.join((
                    '<html><body>',
                    ' <form id="form">',
                    '  <label for="field">Select Field</label>',
                    '  <select id="field" name="field" multiple="multiple">',
                    '    <option value="foo" selected>Foo</option>',
                    '    <option value="bar">Bar</option>',
                    '    <option value="baz">Baz</option>',
                    '  </select>',
                    ' </form>'
                    '</body></html>')))

        self.assertEquals(['foo'], list(browser.find('Select Field').value))
        browser.fill({'Select Field': ['bar', 'baz']})
        self.assertEquals(['bar', 'baz'], list(browser.find('Select Field').value))
