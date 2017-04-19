from ftw.testbrowser import browsing
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestBrowserRequestsMechanize(FunctionalTestCase):

    @browsing
    def test_find_link_by_text(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('link/target', browser.find('A link').attrib['href'])

    @browsing
    def test_find_link_by_text_with_sub_elements(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('link/target',
                          browser.find('A link with sub elements').attrib['href'])

    @browsing
    def test_find_textfield_by_label(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('field value', browser.find('A textfield').value)

    @browsing
    def test_find_textfield_by_name(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('field value', browser.find('textfield').value)

    @browsing
    def test_find_textarea_by_label(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('Text area value', browser.find('A textarea').text)

    @browsing
    def test_find_textarea_by_name(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('Text area value', browser.find('textarea').text)

    @browsing
    def test_find_checkbox_by_label(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals(True, browser.find('Checkbox').checked)

    @browsing
    def test_find_checkbox_by_text(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals(True, browser.find('box').checked)

    @browsing
    def test_find_button_by_label(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals('A button', browser.find('A button').value)

    @browsing
    def test_no_element_found_returns_None(self, browser):
        browser.visit(view='test-elements')
        self.assertEquals(None, browser.find('Something missing'))
