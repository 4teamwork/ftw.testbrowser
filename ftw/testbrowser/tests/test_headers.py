from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from ftw.testbrowser.testing import BROWSER_ZSERVER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestMechanizeHeaders(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_headers(self, browser):
        browser.open()
        self.assertEquals('text/html; charset=utf-8',
                          browser.headers.get('content-type'))


class TestZServerHeaders(TestCase):

    layer = BROWSER_ZSERVER_FUNCTIONAL_TESTING

    @browsing
    def test_headers(self, browser):
        browser.open()
        self.assertEquals('text/html; charset=utf-8',
                          browser.headers.get('content-type'))

    @browsing
    def test_webdav_headers(self, browser):
        browser.webdav('get')
        self.assertEquals('text/html;charset=utf-8',
                          browser.headers.get('content-type'))
