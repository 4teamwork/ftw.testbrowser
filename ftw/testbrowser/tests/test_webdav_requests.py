from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import ZServerRequired
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import MECHANIZE_TESTING
from ftw.testbrowser.testing import REQUESTS_TESTING
from ftw.testbrowser.tests import FunctionalTestCase


class TestWebdavRequests(FunctionalTestCase):
    layer = REQUESTS_TESTING

    @browsing
    def test_login_works(self, browser):
        browser.login().webdav('GET')
        self.assertTrue(plone.logged_in())

    @browsing
    def test_options_request(self, browser):
        browser.webdav('OPTIONS')
        self.assertEquals('1,2', browser.headers.get('DAV'))

    @browsing
    def test_propfind_request(self, browser):
        data = '\n'.join((
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<A:propfind xmlns:A="DAV:">',
                '  <A:prop>',
                '    <A:displayname/>',
                '  </A:prop>',
                '</A:propfind>',
                ))
        browser.login().webdav('PROPFIND', data=data)
        self.assertEquals('Plone site',
                          browser.xpath('//d:displayname').first.text)


class TestNoZserverWebdavRequests(FunctionalTestCase):
    layer = MECHANIZE_TESTING

    @browsing
    def test_webdav_requires_zserver(self, browser):
        with self.assertRaises(ZServerRequired):
            browser.webdav('OPTIONS')
