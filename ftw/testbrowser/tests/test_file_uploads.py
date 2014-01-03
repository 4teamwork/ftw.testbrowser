from StringIO import StringIO
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase
import os.path


class TestFileUploads(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

    @browsing
    def test_tuple_syntax(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'file_file': ('file data', 'foo.txt', 'text/plain')})
        browser.find('Save').click()

        browser.find('foo.txt').click()
        self.assert_file_download('file data')

    @browsing
    def test_stream_syntax(self, browser):
        file_ = StringIO('file data')
        file_.filename = 'foo.txt'
        file_.content_type = 'text/plain'

        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'file_file': file_}).submit()

        browser.find('foo.txt').click()
        self.assert_file_download('file data')

    @browsing
    def test_without_content_type(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'file_file': ('file data', 'foo.txt')}).submit()

        browser.find('foo.txt').click()
        self.assert_file_download('file data')

    @browsing
    def test_filesystem_file_uploading(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')

        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'helloworld.py')
        with open(file_path) as helloworld:
            browser.fill({'Title': 'Hello World',
                          'File': helloworld}).submit()

        browser.find('helloworld.py').click()
        self.assert_file_download('print "Hello World"\n',
                                  filename='helloworld.py',
                                  content_type='text/x-python')

    def assert_file_download(self, data, filename='foo.txt',
                             content_type='text/plain'):
        self.assertEquals(data, browser.contents)
        self.assertEquals('attachment; filename="%s"' % filename,
                          browser.headers.get('Content-Disposition'))
        self.assertEquals('%s; charset=iso-8859-15' % content_type,
                          browser.headers.get('Content-Type'))
