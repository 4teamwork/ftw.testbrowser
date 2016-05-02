from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import OptionsNotFound
from unittest2 import TestCase


WIDGET_HTML = '''
<form>
    <div class="field ArchetypesMultiSelectionWidget "
         data-fieldname="fruits"
         data-uid="7e12016500004fcd80da5279c82f5480"
         id="archetypes-fieldname-fruits">
        <span></span>
        <div class="fieldErrorBox"></div>
        <input type="hidden" value="" name="fruits:default:list" originalvalue="" />
        <div id="fruits">
            <div class="formQuestion label">
                Fruits
                <span class="formHelp" id="fruits_help">Select some fruits</span>
            </div>

            <div class="ArchetypesMultiSelectionValue"
                 id="archetypes-value-fruits_1">
                <input class="blurrable" type="checkbox"
                       name="fruits:list" value="apple" id="fruits_1" />
                <label for="fruits_1">Apple</label>
            </div>

            <div class="ArchetypesMultiSelectionValue"
                 id="archetypes-value-fruits_2">
                <input class="blurrable" type="checkbox"
                       name="fruits:list" value="banana" id="fruits_2" />
                <label for="fruits_2">Banana</label>
            </div>

            <div class="ArchetypesMultiSelectionValue"
                 id="archetypes-value-fruits_3">
                <input class="blurrable" type="checkbox"
                       name="fruits:list" value="watermelon" id="fruits_3" />
                <label for="fruits_3">Watermelon</label>
            </div>

        </div>
    </div>
</form>'''


class TestATMultiSelectionWidget(TestCase):

    @browsing
    def test_filling_file_upload_widget_by_value(self, browser):
        browser.open_html(WIDGET_HTML)
        browser.fill({'Fruits': ['apple', 'banana']})
        self.assertEquals(
            [('fruits:default:list', ''),
             ('fruits:list', 'apple'),
             ('fruits:list', 'banana')],
            browser.css('form').first.form_values())

    @browsing
    def test_filling_file_upload_widget_by_label(self, browser):
        browser.open_html(WIDGET_HTML)
        browser.fill({'Fruits': ['Banana', 'Watermelon']})
        self.assertEquals(
            [('fruits:default:list', ''),
             ('fruits:list', 'banana'),
             ('fruits:list', 'watermelon')],
            browser.css('form').first.form_values())

    @browsing
    def test_reports_unavailable_options_as_exception(self, browser):
        browser.open_html(WIDGET_HTML)
        with self.assertRaises(OptionsNotFound) as cm:
            browser.fill({'Fruits': ['Banana', 'Rhubarb', 'Watermelon']})

        self.assertEquals('Could not find options [\'Rhubarb\']'
                          ' for field "Fruits".'
                          ' Options: "Apple", "Banana", "Watermelon"',
                          str(cm.exception))

    @browsing
    def test_getting_option_labels(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEquals(['Apple', 'Banana', 'Watermelon'],
                          browser.find('Fruits').options)
