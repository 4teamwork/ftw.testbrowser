from ftw.testbrowser import browser
from ftw.testbrowser import exceptions
from unittest2 import TestCase


class TestBrowserExceptions(TestCase):

    def test_browser_not_set_up_exception(self):
        self.assertEquals('The browser is not set up properly.'
                          ' Use the browser as a context manager'
                          ' with the "with" statement.',
                          str(exceptions.BrowserNotSetUpException()))

    def test_form_field_not_found(self):
        self.assertEquals('Could not find form field: "field label".',
                          str(exceptions.FormFieldNotFound('field label')))

    def test_form_field_not_found_with_found_fields(self):
        self.assertEquals('Could not find form field: "field label". '
                          'Fields: "foo", "bar", "baz"',
                          str(exceptions.FormFieldNotFound('field label',
                                                           ['foo', 'bar', 'baz'])))

    def test_options_not_found(self):
        self.assertEquals(
            'Could not find options [\'missing\'] for field "field label".',
            str(exceptions.OptionsNotFound('field label', ['missing'])))

    def test_options_not_found_with_found_options(self):
        self.assertEquals(
            'Could not find options [\'missing\'] for field "field label". '
            'Options: "foo", "bar", "baz"',
            str(exceptions.OptionsNotFound(
                'field label', ['missing'], ['foo', 'bar', 'baz'])))


class TestNoElementFoundException(TestCase):

    def test_no_query_info(self):
        self.assertEqual(
            'Empty result set has no elements.',
            str(exceptions.NoElementFound()))

    def test_query_info_on_browser(self):
        query_info = ('browser', 'css', '.the-link')
        self.assertEqual(
            'Empty result set: browser.css(".the-link") did not match any nodes.',
            str(exceptions.NoElementFound(query_info)))

    def test_query_info_on_node(self):
        with browser:
            browser.open_html('<html><body></body></html>')
            query_info = (browser.css('body').first, 'xpath', '//div')
            self.assertEqual(
                'Empty result set: <NodeWrapper:body, >.xpath("//div") did not'
                ' match any nodes.',
                str(exceptions.NoElementFound(query_info)))
