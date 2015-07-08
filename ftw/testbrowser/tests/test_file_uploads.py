from ftw.testbrowser import Browser
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.tests.helpers import asset
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import SITE_OWNER_NAME
from StringIO import StringIO
from unittest2 import TestCase


class TestFileUploads(TestCase):

    layer = PLONE_ZSERVER

    @browsing
    def test_tuple_syntax(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'file_file': ('file data', 'foo.txt', 'text/plain')})
        browser.find('Save').click()

        browser.find('foo.txt').click()
        self.assert_file_download('file data', browser)

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
        self.assert_file_download('file data', browser)

    @browsing
    def test_without_content_type(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'file_file': ('file data', 'foo.txt')}).submit()

        browser.find('foo.txt').click()
        self.assert_file_download('file data', browser)

    @browsing
    def test_filesystem_file_uploading(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')

        with asset('helloworld.py') as helloworld:
            browser.fill({'Title': 'Hello World',
                          'File': helloworld}).submit()

        browser.find('helloworld.py').click()
        self.assert_file_download('print "Hello World"\n',
                                  filename='helloworld.py',
                                  content_type='text/x-python',
                                  browser=browser)

    @browsing
    def test_binary_file_uploading(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')

        with asset('file.pdf') as pdf:
            browser.fill({'Title': 'The PDF',
                          'File': pdf}).submit()

        browser.find('file.pdf').click()
        self.assert_file_metadata(filename='file.pdf',
                                  content_type='application/pdf',
                                  browser=browser)

        with asset('file.pdf') as pdf:
            self.assertTrue(pdf.read().strip() == browser.contents.strip(),
                            'The PDF was changed when uploaded!')

    def test_requests_library_file_uploads(self):
        with Browser() as browser:
            browser.login(SITE_OWNER_NAME).open(
                view='createObject?type_name=File')
            with asset('helloworld.py') as helloworld:
                browser.fill({'Title': 'Hello World',
                              'File': helloworld}).submit()

            browser.find('helloworld.py').click()
            self.assert_file_download('print "Hello World"\n',
                                      filename='helloworld.py',
                                      content_type='text/x-python',
                                      browser=browser)

    def assert_file_download(self, data, browser, filename='foo.txt',
                             content_type='text/plain'):
        self.assertEquals(data, browser.contents)
        self.assertEquals('attachment; filename="%s"' % filename,
                          browser.headers.get('Content-Disposition'))
        self.assertIn(browser.headers.get('Content-Type'), (
                '%s; charset=iso-8859-15' % content_type,  # mechanize download
                content_type,  # requests lib download
             ))

    def assert_file_metadata(self, browser, filename, content_type):
        self.assertEquals('attachment; filename="%s"' % filename,
                          browser.headers.get('Content-Disposition'))
        self.assertIn(browser.headers.get('Content-Type'), (
                '%s; charset=iso-8859-15' % content_type,  # mechanize download
                content_type,  # requests lib download
                ))
