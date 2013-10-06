from ftw.browser import exceptions
from unittest2 import TestCase


class TestBrowserExceptions(TestCase):

    def test_browser_not_set_up_exception(self):
        self.assertEquals('The browser is not set up properly.'
                          ' Use the browser as a context manager'
                          ' with the "with" statement.',
                          str(exceptions.BrowserNotSetUpException()))
