from ftw.testbrowser import browsing
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestXMLDocument(BrowserTestCase):

    @browsing
    def test_utf8_document_with_umlaut(self, browser):
        browser.open(view='test-asset', data={'filename': 'cities-utf8.xml'})
        self.assertEqual('text/xml; charset=utf-8',
                         browser.contenttype)
        self.assertEqual('cities',
                         browser.document.getroot().tag)
        self.assertEqual([u'Bern', u'Z\xfcrich', u'Basel'],
                         browser.css('city').text)

    @browsing
    def test_ISO_8859_1_document_with_umlaut(self, browser):
        browser.open(view='test-asset', data={'filename': 'cities-iso-8859-1.xml'})
        self.assertEqual('text/xml; charset=ISO-8859-1',
                         browser.contenttype)
        self.assertEqual('cities',
                         browser.document.getroot().tag)
        self.assertEqual([u'Bern', u'Z\xfcrich', u'Basel'],
                         browser.css('city').text)

    @browsing
    def test_reparse_with_html_parse(self, browser):
        browser.open(view='test-asset', data={'filename': 'cities-iso-8859-1.xml'})
        self.assertEqual('cities', browser.document.getroot().tag)
        browser.parse_as_html()
        self.assertEqual('html', browser.document.getroot().tag)
        browser.parse_as_xml()
        self.assertEqual('cities', browser.document.getroot().tag)
