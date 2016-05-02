# -*- coding: utf-8 -*-
from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import OptionsNotFound
from unittest2 import TestCase


"""Tests the default choice collection widget.
Example for building a field / widget as used in this test:

from zope import schema
from zope.interface import Interface
from zope.schema.vocabulary import SimpleVocabulary

class ISchema(Interface):
    fuits = schema.List(
        title=u'Fruits',
        value_type=schema.Choice(
            vocabulary=SimpleVocabulary.fromValues(
                [u'Apple', u'Banana', u'Watermelon'])))

"""


WIDGET_HTML = '''
<form>
  <div data-fieldname="form.widgets.fruits" class="field z3cformInlineValidation kssattr-fieldname-form.widgets.fruits error empty" id="formfield-form-widgets-fruits">
    <label for="form-widgets-fruits" class="horizontal">
      Fruits
      <span class="required horizontal" title="Required">&nbsp;</span>
    </label>

    <table border="0" class="ordered-selection-field" id="form-widgets-fruits">
      <tbody>
        <tr>
          <td>
            <select id="form-widgets-fruits-from" name="form.widgets.fruits.from" class="required list-field" multiple="multiple" size="5">
              <option value="/fruits/apple">Apple</option>
              <option value="/fruits/watermelon">Watermelon</option>
            </select>
          </td>
          <td>
            <button onclick="" name="from2toButton" type="button" value="→">→</button>
            <br />
            <button onclick="" name="to2fromButton" type="button" value="←">←</button>
          </td>
          <td>
            <select id="form-widgets-fruits-to" name="form.widgets.fruits.to" class="required list-field" multiple="multiple" size="5">
              <option value="/fruits/banana" selected="selected">Banana</option>
            </select>
            <span id="form-widgets-fruits-toDataContainer">
            </span>
          </td>
          <td>
            <button onclick="" name="upButton" type="button" value="↑">↑</button>
            <br />
            <button onclick="" name="downButton" type="button" value="↓">↓</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</form>'''


class TestZ3cChoiceCollectionWidget(TestCase):

    @browsing
    def test_options_selected(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            [('/fruits/banana', 'Banana')],
            browser.find('Fruits').selected)

    @browsing
    def test_options_selected_labels(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            ['Banana'],
            browser.find('Fruits').selected_labels)

    @browsing
    def test_options_selected_values(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            ['/fruits/banana'],
            browser.find('Fruits').selected_values)

    @browsing
    def test_options_unselected(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            [('/fruits/apple', 'Apple'),
             ('/fruits/watermelon', 'Watermelon')],
            browser.find('Fruits').unselected)

    @browsing
    def test_options_unselected_labels(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            ['Apple', 'Watermelon'],
            browser.find('Fruits').unselected_labels)

    @browsing
    def test_options_unselected_values(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            ['/fruits/apple', '/fruits/watermelon'],
            browser.find('Fruits').unselected_values)

    @browsing
    def test_options_returns_selected_and_unselected_options(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            [('/fruits/apple', 'Apple'),
             ('/fruits/watermelon', 'Watermelon'),
             ('/fruits/banana', 'Banana')],
            browser.find('Fruits').options)

    @browsing
    def test_options_labels(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            ['Apple', 'Watermelon', 'Banana'],
            browser.find('Fruits').options_labels)

    @browsing
    def test_options_values(self, browser):
        browser.open_html(WIDGET_HTML)
        self.assertEqual(
            ['/fruits/apple', '/fruits/watermelon', '/fruits/banana'],
            browser.find('Fruits').options_values)

    @browsing
    def test_selecting_multiple_options_by_label(self, browser):
        browser.open_html(WIDGET_HTML)
        browser.fill({'Fruits': ['Apple', 'Banana']})

        self.assertEquals(
            [('form.widgets.fruits:list', '/fruits/apple'),
             ('form.widgets.fruits:list', '/fruits/banana')],
            browser.css('form').first.form_values())

        self.assertEqual(
            ['Apple', 'Banana'],
            browser.find('Fruits').selected_labels)
        self.assertEqual(
            ['Watermelon'],
            browser.find('Fruits').unselected_labels)

    @browsing
    def test_selecting_options_respects_selection_order(self, browser):
        browser.open_html(WIDGET_HTML)
        browser.fill({'Fruits': ['Banana', 'Apple']})

        self.assertEquals(
            [('form.widgets.fruits:list', '/fruits/banana'),
             ('form.widgets.fruits:list', '/fruits/apple')],
            browser.css('form').first.form_values())
        self.assertEqual(
            ['Banana', 'Apple'],
            browser.find('Fruits').selected_labels)

    @browsing
    def test_selecting_single_option_by_label(self, browser):
        browser.open_html(WIDGET_HTML)
        browser.fill({'Fruits': 'Apple'})

        self.assertEquals(
            [('form.widgets.fruits:list', '/fruits/apple')],
            browser.css('form').first.form_values())

        self.assertEqual(
            ['Apple'],
            browser.find('Fruits').selected_labels)
        self.assertEqual(
            ['Watermelon', 'Banana'],
            browser.find('Fruits').unselected_labels)

    @browsing
    def test_selecting_multiple_options_by_values(self, browser):
        browser.open_html(WIDGET_HTML)
        browser.fill({'Fruits': ['/fruits/apple', '/fruits/banana']})

        self.assertEquals(
            [('form.widgets.fruits:list', '/fruits/apple'),
             ('form.widgets.fruits:list', '/fruits/banana')],
            browser.css('form').first.form_values())

        self.assertEqual(
            ['Apple', 'Banana'],
            browser.find('Fruits').selected_labels)
        self.assertEqual(
            ['Watermelon'],
            browser.find('Fruits').unselected_labels)

    @browsing
    def test_reports_unavailable_options_as_exception(self, browser):
        browser.open_html(WIDGET_HTML)
        with self.assertRaises(OptionsNotFound) as cm:
            browser.fill({'Fruits': ['Banana', 'Rhubarb', 'Watermelon']})

        self.assertEquals('Could not find options [\'Rhubarb\']'
                          ' for field "Fruits".'
                          ' Options: "Apple", "Watermelon", "Banana"',
                          str(cm.exception))

    @browsing
    def test_selecting_with_plone_42(self, browser):
        # The data-fieldname attribute is available from Plone>=4.3
        browser.open_html(WIDGET_HTML.replace('data-fieldname', 'removed'))
        browser.fill({'Fruits': 'Apple'})

        self.assertEquals(
            [('form.widgets.fruits:list', '/fruits/apple')],
            browser.css('form').first.form_values())

        self.assertEqual(
            ['Apple'],
            browser.find('Fruits').selected_labels)
        self.assertEqual(
            ['Watermelon', 'Banana'],
            browser.find('Fruits').unselected_labels)
