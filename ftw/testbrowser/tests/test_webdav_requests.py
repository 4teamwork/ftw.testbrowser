from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.exceptions import NoWebDAVSupport
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import MECHANIZE_TESTING
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.alldrivers import skip_driver


@all_drivers
class TestWebdavRequests(BrowserTestCase):

    @skip_driver(LIB_MECHANIZE, 'Mechanize does not support webdav.')
    @browsing
    def test_login_works(self, browser):
        browser.login().webdav('GET')
        self.assertTrue(plone.logged_in())

    @skip_driver(LIB_MECHANIZE, 'Mechanize does not support webdav.')
    @browsing
    def test_options_request(self, browser):
        browser.webdav('OPTIONS')
        self.assertEquals('1,2', browser.headers.get('DAV'))

    @skip_driver(LIB_MECHANIZE, 'Mechanize does not support webdav.')
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


class TestNoZserverWebdavRequests(BrowserTestCase):
    layer = MECHANIZE_TESTING

    @browsing
    def test_webdav_requires_zserver(self, browser):
        with self.assertRaises(NoWebDAVSupport):
            browser.webdav('OPTIONS')
