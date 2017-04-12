from ftw.testbrowser import browsing
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestXMLDocument(FunctionalTestCase):

    @browsing
    def test_utf8_document_with_umlaut(self, browser):
        browser.open(view='test-asset', data={'filename': 'cities-utf8.xml'})
        self.assertEquals('text/xml; charset=utf-8',
                          browser.contenttype)
        self.assertEquals('cities',
                          browser.document.getroot().tag)
        self.assertEquals([u'Bern', u'Z\xfcrich', u'Basel'],
                          browser.css('city').text)

    @browsing
    def test_ISO_8859_1_document_with_umlaut(self, browser):
        browser.open(view='test-asset', data={'filename': 'cities-iso-8859-1.xml'})
        self.assertEquals('text/xml; charset=ISO-8859-1',
                          browser.contenttype)
        self.assertEquals('cities',
                          browser.document.getroot().tag)
        self.assertEquals([u'Bern', u'Z\xfcrich', u'Basel'],
                          browser.css('city').text)

    @browsing
    def test_reparse_with_html_parse(self, browser):
        browser.open(view='test-asset', data={'filename': 'cities-iso-8859-1.xml'})
        self.assertEquals('cities', browser.document.getroot().tag)
        browser.parse_as_html()
        self.assertEquals('html', browser.document.getroot().tag)
        browser.parse_as_xml()
        self.assertEquals('cities', browser.document.getroot().tag)
