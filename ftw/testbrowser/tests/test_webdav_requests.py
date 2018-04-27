from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.exceptions import NoWebDAVSupport
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import MECHANIZE_TESTING
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.alldrivers import skip_driver
from lxml import etree
from plone.app.testing import SITE_OWNER_NAME


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

    @skip_driver(LIB_MECHANIZE, 'Mechanize does not support webdav.')
    @browsing
    def test_browser_corrects_webdav_lock_namespacing_bug(self, browser):
        data = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<D:lockinfo xmlns:D="DAV:">\n'
            '  <D:lockscope><D:exclusive/></D:lockscope>\n'
            '  <D:locktype><D:write/></D:locktype>\n'
            '  <D:owner>\n'
            '  <D:href>Test Token</D:href>\n'
            '  </D:owner>\n'
            '</D:lockinfo>'
            )
        browser.login(SITE_OWNER_NAME).open()
        document = create(Builder('document').titled(u'Foo'))
        browser.login(SITE_OWNER_NAME).webdav('LOCK', document, data=data)
        # response contains wrong namespace for the lock token
        self.assertIn("<D:href>Test Token</D:href>", browser.contents)
        # this is corrected in parsed contents
        self.assertIn("<d:href>Test Token</d:href>", etree.tostring(browser.document))
        self.assertEqual("Test Token", browser.document.find('.//{DAV:}href').text)


class TestNoZserverWebdavRequests(BrowserTestCase):
    layer = MECHANIZE_TESTING

    @browsing
    def test_webdav_requires_zserver(self, browser):
        with self.assertRaises(NoWebDAVSupport):
            browser.webdav('OPTIONS')
