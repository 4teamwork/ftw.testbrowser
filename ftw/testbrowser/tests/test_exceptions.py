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
