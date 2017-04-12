from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.form import Form
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.widgets.base import PloneWidget
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
import lxml.html


@all_drivers
class TestBrowserForms(FunctionalTestCase):

    @browsing
    def test_find_form_by_field_label(self, browser):
        browser.open(view='login_form')
        self.assertEquals(Form, type(browser.find_form_by_fields('Login Name')))

    @browsing
    def test_exception_when_field_not_found(self, browser):
        browser.open(view='login_form')
        with self.assertRaises(FormFieldNotFound) as cm:
            browser.find_form_by_fields('First Name')
        self.assertTrue(
            str(cm.exception).startswith('Could not find form field: "First Name".'
                                         ' Fields: '),
            str(cm.exception))

    @browsing
    def test_exception_when_chaning_fields_in_different_forms(self, browser):
        browser.open(view='login_form')
        with self.assertRaises(AmbiguousFormFields):
            browser.find_form_by_fields('Login Name', 'Search Site')

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
    def test_fill_field(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': 'The Folder'}).save()
        self.assertEquals('listing_view', plone.view())
        self.assertEquals('The Folder', plone.first_heading())

    @browsing
    def test_fill_field_with_unicode_umlauts(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': u'F\xf6lder',
                      'Summary': u'The f\xf6lder description'}).save()
        self.assertEquals('listing_view', plone.view())
        self.assertEquals(u'F\xf6lder', plone.first_heading())

    @browsing
    def test_fill_field_with_utf8_umlauts(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        browser.fill({'Title': u'F\xf6lder'.encode('utf-8'),
                      'Summary': u'The f\xf6lder description'.encode('utf-8')}).save()
        self.assertEquals('listing_view', plone.view())
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
    def test_save_add_form(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': 'The page'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals(browser.url,
                          self.portal.portal_url() + '/the-page/view')

    @browsing
    def test_find_submit_buttons(self, browser):
        browser.open(view='login_form')
        form = browser.find_form_by_field('Login Name')
        button = form.find_submit_buttons().first
        self.assertEquals('Log in', button.value)

    @browsing
    def test_find_widget(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        form = browser.find_form_by_fields('Title')
        widget = form.find_widget('Title')
        self.assertEquals('div', widget.tag)
        self.assertEquals(PloneWidget, type(widget))

    @browsing
    def test_action_url__fqdn(self, browser):
        browser.open_html(
            '<html>'
            ' <form action="http://localhost/foo" id="form"></form>'
            '</html>')
        form = browser.css('#form').first
        self.assertEquals('http://localhost/foo', form.action_url)

    @browsing
    def test_action_url__non_fqdn_relative_to_base_doc(self, browser):
        browser.open_html(
            '<html>'
            ' <base href="http://localhost/foo">'
            ' <form action="bar" id="form"></form>'
            '</html>')
        form = browser.css('#form').first
        self.assertEquals('http://localhost/bar', form.action_url)

    @browsing
    def test_action_url__non_fqdn_relative_to_base_folder(self, browser):
        browser.open_html(
            '<html>'
            ' <base href="http://localhost/foo/">'
            ' <form action="bar" id="form"></form>'
            '</html>')
        form = browser.css('#form').first
        self.assertEquals('http://localhost/foo/bar', form.action_url)

    @browsing
    def test_action_url__non_fqdn_relative_to_base_with_dot(self, browser):
        browser.open_html(
            '<html>'
            ' <base href="http://localhost/foo/">'
            ' <form action="./bar" id="form"></form>'
            '</html>')
        form = browser.css('#form').first
        self.assertEquals('http://localhost/foo/bar', form.action_url)

    @browsing
    def test_action_url__non_fqdn_absolute_to_base(self, browser):
        browser.open_html(
            '<html>'
            ' <base href="http://localhost/foo/bar">'
            ' <form action="/baz" id="form"></form>'
            '</html>')
        form = browser.css('#form').first
        self.assertEquals('http://localhost/baz', form.action_url)

    @browsing
    def test_action_url__no_action_uses_browser_url(self, browser):
        url = self.layer['portal'].absolute_url() + '/folder_contents'

        browser.login(SITE_OWNER_NAME).open(url)
        browser.parse(
            '<html>'
            ' <form id="form"></form>'
            '</html>')
        self.assertEquals(url, browser.url)

        form = browser.css('#form').first
        self.assertEquals(url, form.action_url)


@all_drivers
class TestSubmittingForms(FunctionalTestCase):

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

    @browsing
    def test_submitting_GET_form(self, browser):
        browser.visit(view='test-form')
        browser.fill({'atext': 'foo'}).submit()
        self.assertEquals({'atext': 'foo',
                           'formmethod': 'GET',
                           'submit-button': 'Submit'}, browser.json)
        self.assertEquals(
            '{}/test-form-result?formmethod=GET&atext=foo&submit-button=Submit'
            .format(self.portal.portal_url()),
            browser.url)

    @browsing
    def test_find_submit_button_tag(self, browser):
        browser.open_html(
            '<form>'
            '<button type="submit">blubb</button>'
            '</form>')
        form = browser.forms['form-0']
        self.assertEquals(1, len(form.find_submit_buttons()))

    @browsing
    def test_find_submit_button_tag_by_label(self, browser):
        browser.open_html(
            '<form>'
            '<button type="submit">blubb</button>'
            '</form>')
        form = browser.forms['form-0']
        button = form.find_button_by_label('blubb')
        self.assertTrue(button)
        self.assertEquals('submit', button.type)

    @browsing
    def test_find_submit_button_tag_click(self, browser):
        browser.open()
        browser.parse(
            '<form action="{}">'.format(self.portal.portal_url()) +
            '<button type="submit">blubb</button>'
            '</form>')
        form = browser.forms['form-0']
        button = form.find_button_by_label('blubb')
        button.click()

    @browsing
    def test_find_submit_button_tag_in_request(self, browser):
        browser.visit(view='test-form')
        browser.find("novalue-button").click()
        self.assertEquals({'textfield': '',
                           'novalue-button': ''}, browser.json)


@all_drivers
class TestSelectField(FunctionalTestCase):

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
    def test_verbose_message_when_no_option_matches(self, browser):
        browser.open_html(u'\n'.join((
            u'<html><body>',
            u' <form id="form">',
            u'  <label for="field">Select Field</label>',
            u'  <select id="field" name="field">',
            u'    <option value="">Please choose\u2026</option>',
            u'    <option value="foo">Foo</option>',
            u'    <option value="bar">Bar</option>',
            u'  </select>',
            u' </form>'
            u'</body></html>')))

        with self.assertRaises(ValueError) as cm:
            browser.fill({'Select Field': 'baz'})

        self.assertEquals(
            u'No option u\'baz\' for select "field". '
            u'Available options: "Please choose\u2026" (), '
            u'"Foo" (foo), "Bar" (bar).',
            cm.exception.message)

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

    @browsing
    def test_getting_options_items(self, browser):
        browser.open_html(
            '<form>'
            ' <label for="field">Field</label>'
            ' <select id="field" name="field">'
            '  <option value="foo">Foo</option>'
            '  <option value="bar">Bar</option>'
            ' </select>'
            '</form>')

        self.assertEquals([('foo', 'Foo'), ('bar', 'Bar')],
                          browser.find('Field').options)

    @browsing
    def test_getting_options_labels(self, browser):
        browser.open_html(
            '<form>'
            ' <label for="field">Field</label>'
            ' <select id="field" name="field">'
            '  <option value="foo">Foo</option>'
            '  <option value="bar">Bar</option>'
            ' </select>'
            '</form>')

        self.assertEquals(['Foo', 'Bar'],
                          browser.find('Field').options_labels)

    @browsing
    def test_getting_options_values(self, browser):
        browser.open_html(
            '<form>'
            ' <label for="field">Field</label>'
            ' <select id="field" name="field">'
            '  <option value="foo">Foo</option>'
            '  <option value="bar">Bar</option>'
            ' </select>'
            '</form>')

        self.assertEquals(['foo', 'bar'],
                          browser.find('Field').options_values)

    @browsing
    def test_simple_textarea_does_not_break(self, browser):
        """Regression: A <textarea> without id-attribute / label used to break
        loading the page.
        """
        browser.open_html(
            '<form>'
            ' <textarea name="text"></textarea>'
            '</form>')
        form = browser.fill({'text': 'some text'})
        self.assertEqual({'text': 'some text'}, dict(form.values))
