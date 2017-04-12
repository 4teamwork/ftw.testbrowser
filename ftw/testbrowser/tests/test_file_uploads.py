from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import asset
from plone.app.testing import SITE_OWNER_NAME
from StringIO import StringIO
from unittest2 import TestCase


@all_drivers
class TestFileUploadsArchetypes(TestCase):

    @browsing
    def test_tuple_syntax(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'File': ('file data', 'foo.txt', 'text/plain')}).save()

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
                      'File': file_}).save()

        browser.find('foo.txt').click()
        self.assert_file_download('file data', browser)

    @browsing
    def test_without_content_type(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'foo',
                      'File': ('file data', 'foo.txt')}).save()

        browser.find('foo.txt').click()
        self.assert_file_download('file data', browser)

    @browsing
    def test_filesystem_file_uploading(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')

        with asset('helloworld.py') as helloworld:
            browser.fill({'Title': 'Hello World',
                          'File': helloworld}).save()

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
                          'File': pdf}).save()

        browser.find('file.pdf').click()
        self.assert_file_metadata(filename='file.pdf',
                                  content_type='application/pdf',
                                  browser=browser)

        with asset('file.pdf') as pdf:
            self.assertTrue(pdf.read().strip() == browser.contents.strip(),
                            'The PDF was changed when uploaded!')

    def assert_file_download(self, data, browser, filename='foo.txt',
                             content_type='text/plain'):
        self.assertEquals(data, browser.contents)
        self.assert_file_metadata(browser,
                                  filename=filename,
                                  content_type=content_type)

    def assert_file_metadata(self, browser, filename, content_type):
        self.assertIn(
            browser.headers.get('Content-Disposition'),
            ('attachment; filename="%s"' % filename,
             'attachment; filename*=UTF-8\'\'%s' % filename))
        self.assertIn(browser.headers.get('Content-Type'), (
            '%s; charset=iso-8859-15' % content_type,  # mechanize download
            content_type,  # requests lib download
        ))
