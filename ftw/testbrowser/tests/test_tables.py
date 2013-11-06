from ftw.testbrowser import browsing
from ftw.testbrowser.table import colspan_padded_text
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestTables(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_find_cell_by_text_on_table(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#onecol-table').first
        cell = table.head_rows[0].css('>th').first
        self.assertEquals(cell, table.find('Foo'))

    @browsing
    def test_table_as_lists(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [['Product', 'Price'],
             ['Socks', '12.90'],
             ['Pants', '35.00'],
             ['TOTAL:', '47.90']],
            browser.css('#simple-table').first.lists())

    @browsing
    def test_table_as_lists_without_header(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [['Socks', '12.90'],
             ['Pants', '35.00'],
             ['TOTAL:', '47.90']],
            browser.css('#simple-table').first.lists(head=False))

    @browsing
    def test_table_as_lists_without_body(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [['Product', 'Price'],
             ['TOTAL:', '47.90']],
            browser.css('#simple-table').first.lists(body=False))

    @browsing
    def test_table_as_lists_without_footer(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [['Product', 'Price'],
             ['Socks', '12.90'],
             ['Pants', '35.00']],
            browser.css('#simple-table').first.lists(foot=False))

    @browsing
    def test_table_as_lists_with_colspan(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [['Product', 'Product', 'Price'],
             ['Name', 'Category', 'CHF'],
             ['Fancy Pants', 'Pants', '44.80'],
             ['Pink Pullover', 'Pullovers', '69.90'],
             ['TOTAL:', 'TOTAL:', '114.70']],
            browser.css('#advanced-table').first.lists())

    @browsing
    def test_table_as_dicts(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [{'Product': 'Socks',
              'Price': '12.90'},
             {'Product': 'Pants',
              'Price': '35.00'},
             {'Product': 'TOTAL:',
              'Price': '47.90'}],
            browser.css('#simple-table').first.dicts())

    @browsing
    def test_table_as_dicts_without_footer(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [{'Product': 'Socks',
              'Price': '12.90'},
             {'Product': 'Pants',
              'Price': '35.00'}],
            browser.css('#simple-table').first.dicts(foot=False))

    @browsing
    def test_table_as_dicts_without_body(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [{'Product': 'TOTAL:',
              'Price': '47.90'}],
            browser.css('#simple-table').first.dicts(body=False))

    @browsing
    def test_table_as_dicts_with_colspan(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            [{'Product\nName': 'Fancy Pants',
              'Product\nCategory': 'Pants',
              'Price\nCHF': '44.80'},
             {'Product\nName': 'Pink Pullover',
              'Product\nCategory': 'Pullovers',
              'Price\nCHF': '69.90'},
             {'Product\nName': 'TOTAL:',
              'Product\nCategory': 'TOTAL:',
              'Price\nCHF': '114.70'}],

            browser.css('#advanced-table').first.dicts())

    @browsing
    def test_titles(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#simple-table').first
        self.assertEquals(['Product', 'Price'], table.titles)

    @browsing
    def test_titles__multi_rows(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#advanced-table').first
        self.assertEquals(['Product\nName', 'Product\nCategory', 'Price\nCHF'],
                          table.titles)

    @browsing
    def test_head_rows(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            ['Foo'],
            browser.css('#onecol-table').first.head_rows.normalized_text())

    @browsing
    def test_head_rows_filters_unfamiliars(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#nested-table').first
        cells = table.head_rows.css('>td')
        self.assertEquals(
            ['Heading'],
            cells.normalized_text(recursive=False))

    @browsing
    def test_foot_rows(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            ['Baz'],
            browser.css('#onecol-table').first.foot_rows.normalized_text())

    @browsing
    def test_foot_rows_filters_unfamiliars(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#nested-table').first
        cells = table.foot_rows.css('>td')
        self.assertEquals(
            ['Footer'],
            cells.normalized_text(recursive=False))

    @browsing
    def test_body_rows(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            ['Bar'],
            browser.css('#onecol-table').first.body_rows.normalized_text())

    @browsing
    def test_body_rows_filters_unfamiliars(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#nested-table').first
        cells = table.body_rows.css('>td')
        self.assertEquals(
            ['Body'],
            cells.normalized_text(recursive=False))

    @browsing
    def test_rows(self, browser):
        browser.open(view='test-tables')
        self.assertEquals(
            ['Foo', 'Baz', 'Bar'],
            browser.css('#onecol-table').first.rows.normalized_text())

    @browsing
    def test_rows_filters_unfamiliars(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#nested-table').first
        cells = table.rows.css('>td')
        self.assertEquals(
            ['Heading', 'Footer', 'Body'],
            cells.normalized_text(recursive=False))

    @browsing
    def test_get_rows__head(self, browser):
        browser.open(view='test-tables')
        rows = browser.css('#nested-table').first.get_rows(head=True)
        self.assertEquals(['Heading'],
                          rows.css('>td').normalized_text(recursive=False))

    @browsing
    def test_get_rows__body(self, browser):
        browser.open(view='test-tables')
        rows = browser.css('#nested-table').first.get_rows(body=True)
        self.assertEquals(['Body'],
                          rows.css('>td').normalized_text(recursive=False))

    @browsing
    def test_get_rows__foot(self, browser):
        browser.open(view='test-tables')
        rows = browser.css('#nested-table').first.get_rows(foot=True)
        self.assertEquals(['Footer'],
                          rows.css('>td').normalized_text(recursive=False))

    @browsing
    def test_get_rows__body_and_foot(self, browser):
        browser.open(view='test-tables')
        rows = browser.css('#nested-table').first.get_rows(body=True, foot=True)
        self.assertEquals(['Body', 'Footer'],
                          rows.css('>td').normalized_text(recursive=False))

    @browsing
    def test_cells_attribute_contains_all_table_cells(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#onecol-table').first
        self.assertEquals(table.css('td, th'),
                          table.cells)

    @browsing
    def test_is_familiar(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#nested-table').first
        self.assertFalse(table.is_familiar(table.css('td table td').first))
        self.assertTrue(table.is_familiar(table.css('td').first))

    @browsing
    def test_colspan_padded_text(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#advanced-table').first
        foot_row = table.foot_rows.first

        # The "TOTAL:" cell has colspan="2"
        self.assertEquals(
            {'normal': ['TOTAL:', '114.70'],
             'padded': ['TOTAL:', 'TOTAL:', '114.70']},

            {'normal': foot_row.css('>td').normalized_text(),
             'padded': colspan_padded_text(foot_row)})


class TestTableRow(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_table_attribute_is_table_object(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#simple-table').first
        self.assertEquals(table, table.css('tr').first.table)

    @browsing
    def test_cells_attribute_contains_all_cells(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#nested-table').first
        row = table.body_rows[0]
        cells = row.css('>td')
        self.assertEquals(cells, row.cells)

    @browsing
    def test_row_as_dict(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#simple-table').first
        row = table.body_rows[0]
        self.assertEquals({'Product': 'Socks',
                           'Price': '12.90'},
                          row.dict())

    @browsing
    def test_row_as_dict_with_colspan(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#advanced-table').first
        row = table.foot_rows[0]
        # colspan is repeated, therefore we have two "TOTAL:"
        self.assertEquals({'Product\nName': 'TOTAL:',
                           'Product\nCategory': 'TOTAL:',
                           'Price\nCHF': '114.70'},
                          row.dict())


class TestTableCell(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_table_attribute_is_table_object(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#simple-table').first
        self.assertEquals(table, table.css('tr').first.table)

    @browsing
    def test_row_attribute_is_table_row_node(self, browser):
        browser.open(view='test-tables')
        table = browser.css('#onecol-table').first
        row = table.body_rows[0]
        self.assertEquals(row, row.cells.first.row)
