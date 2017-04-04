from ftw.testbrowser.testing import BROWSER_ZSERVER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class FunctionalTestCase(TestCase):
    layer = BROWSER_ZSERVER_FUNCTIONAL_TESTING

    def assert_starts_with(self, start, contents):
        self.assertTrue(
            contents.startswith(start),
            'Expected browser.contents to start with "{0}",'
            ' but it is starting with "{1}"'.format(
                start, contents[:len(start)]))
