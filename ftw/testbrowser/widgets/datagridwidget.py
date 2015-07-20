from copy import deepcopy
from ftw.testbrowser.nodes import wrap_node
from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
from lxml import etree
from lxml.html import formfill


@widget
class DataGridWidget(PloneWidget):

    @staticmethod
    def match(node):
        if not node.tag == 'div' or 'field' not in node.classes:
            return False
        return bool(node.css('table.datagridwidget-table-view'))

    def fill(self, values):
        self.clear()
        map(self.append, values)

    def clear(self):
        empty_row = self.empty_row
        for row in self.table.body_rows[:]:
            if row == empty_row:
                continue

            row.node.getparent().remove(row.node)
        self.counter.attrib['value'] = '0'

    def append(self, row_values):
        row = wrap_node(deepcopy(self.empty_row.node), self.browser)
        row.attrib['class'] = 'datagridwidget-row'

        titles = map(lambda title: title.rstrip('*').rstrip(),
                     self.table.titles)
        cells_by_label = dict(zip(titles, row.css('>td')))
        for label, value in row_values.items():
            assert label in cells_by_label, \
                ('DataGridField: column with label "{0}" not found.\n'
                 'Columns: {1}').format(label, sorted(cells_by_label.keys()))

            self._fill_cell(cells_by_label[label], label, value)

        row_index = len(self.table.body_rows) - 1  # Before the template row.
        for node in row.css('[name^="{0}"]'.format(self.fieldname)):
            node.attrib['name'] = node.attrib['name'].replace(
                '.TT', '.{0}'.format(row_index))

        self.table.css('tbody').first.node.insert(-1, row.node)
        self.counter.attrib['value'] = str(
            int(self.counter.attrib['value']) + 1)

    @property
    def table(self):
        if '_table' not in dir(self):
            self._table = self.css('.datagridwidget-table-view').first
        return self._table

    @property
    def empty_row(self):
        return self.table.css('tr.datagridwidget-empty-row').first

    @property
    def counter(self):
        return self.css('input[name="{0}.count"]'.format(self.fieldname)).first

    def _fill_cell(self, cell, label, value):
        handlers = (
            ('div.autocompleteInputWidget', self._fill_autocomplete),
            ('input[type=text]', self._fill_text),
            ('select', self._fill_select),
            ('input[type=checkbox]', self._fill_checkbox),
        )

        for selector, func in handlers:
            fields = cell.css(selector)
            if len(fields) == 1:
                return func(fields.first, value)

        raise Exception('DataGridField: unknown column type "{0}"'.format(
            label))

    def _fill_text(self, node, value):
        return formfill._fill_single(node.node, value)

    def _fill_select(self, node, value):
        node.value = value

    def _fill_checkbox(self, node, value):
        if value:
            value = node.attrib['value']
        else:
            value = ''
        return formfill._fill_multiple(node, value)

    def _fill_autocomplete(self, node, values):
        if not isinstance(values, (list, set, tuple)):
            values = [values]
        values = map(self._resolve_objects_to_path, values)

        # remove currently selected values
        for span in node.css('span.option'):
            span.node.getparent().remove(span.node)

        fieldname = node.css('[name$="empty-marker"]').first.attrib.get(
            'name').replace('-empty-marker', '')
        for value in values:
            span = etree.SubElement(node.node, 'span',
                                    {'class': 'option'})
            etree.SubElement(span, 'input', {
                'type': 'checkbox',
                'name': fieldname,
                'value': value,
                'checked': 'checked'})
            etree.SubElement(span, 'label').text = value

    def _resolve_objects_to_path(self, value):
        if hasattr(value, 'getPhysicalPath'):
            return '/'.join(value.getPhysicalPath())
        else:
            return value
