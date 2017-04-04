from ftw.testbrowser import jsbrowsing
from ftw.testbrowser.tests import FunctionalTestCase


class TestPhantomJS(FunctionalTestCase):

    @jsbrowsing
    def test_load_page(self, browser):
        browser.open()
        self.assert_starts_with('<!DOCTYPE html>', browser.contents.strip())
