from contextlib import contextmanager
from ftw.testbrowser import browsing
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests import IS_PLONE_5
from ftw.testbrowser.tests.alldrivers import all_drivers
from unittest import skipUnless
import os


@all_drivers
@skipUnless(IS_PLONE_5, 'folder_contents in plone 5 is js only.')
class TestPlone5DisableResourceRegistries(BrowserTestCase):
    """In Plone 5, bundling the resources takes too much time in testing.
    ftw.testbrowser just disables the viewlets for JS and CSS for making it faster.
    ftw.testbrowser does nothing with JS and CSS as it is not a full browser.
    """

    @browsing
    def test_no_resource_registry_viewlets_by_default(self, browser):
        browser.open()
        self.assertFalse(browser.css('script'))

    @browsing
    def test_enable_resource_registries_by_environment_variable(self, browser):

        with self.env('TESTBROWSER_DISABLE_RESOURCE_REGISTRIES', 'false'):
            browser.open()
            self.assertTrue(browser.css('script'))

    @browsing
    def test_enable_by_flag(self, browser):
        browser.disable_resource_registries = False
        browser.open()
        self.assertTrue(browser.css('script'))

    @contextmanager
    def env(self, name, value):
        self.assertNotIn(name, os.environ,
                         'environment variable unexpectedly set')
        os.environ[name] = value
        try:
            yield
        finally:
            os.environ.pop(name)
