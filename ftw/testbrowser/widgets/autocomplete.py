from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
from lxml import etree
from plone.uuid.interfaces import IUUID
import re


@widget
class AutocompleteWidget(PloneWidget):
    """Represents the autocomplete widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        return len(node.css('div.autocompleteInputWidget')) > 0

    @classmethod
    def find_widget_in_datagrid_cell(kls, cell):
        if len(cell.css('div.autocompleteInputWidget')) > 0:
            return kls(cell, cell.browser)
        else:
            return None

    def fill(self, values):
        """Fill the autocomplete value with a key from the vocabulary.
        For content tree widgets, the value may be a Plone object which
        will be replaced with the object path.

        :param values: value to fill the autocomplete field with.
        :type values: string or object
        """
        if not isinstance(values, (list, set, tuple)):
            values = [values]

        values = self._resolve_objects_to_path(values)

        container = self.css('div.autocompleteInputWidget').first

        if self.fieldname is None:
            # We are in a datagrid field and self is not a div.field
            fieldname = (container.css('[name$="empty-marker"]').first
                         .attrib.get('name').replace('-empty-marker', ''))
        else:
            fieldname = '%s:list' % self.fieldname

        # remove currently selected values
        for span in container.css('span.option'):
            span.node.getparent().remove(span.node)

        # add new values
        for value in values:
            span = etree.SubElement(container.node, 'span',
                                    {'class': 'option'})
            etree.SubElement(span, 'input', {
                    'type': 'checkbox',
                    'name': fieldname,
                    'value': value,
                    'checked': 'checked'})
            etree.SubElement(span, 'label').text = value

    def query(self, query_string):
        """Make a query request to the autocomplete vocabulary.

        :param query_string: Search string to query with.
        :type query_string: string
        :returns: List of results, each as a tuple with token and label.
        :rtype: list of tuple of strings.

        """

        url = self._get_query_url()

        with self.browser.clone() as query_browser:
            query_browser.open(url, data={'q': query_string})
            return map(lambda line: line.split('|'),
                       query_browser.contents.split('\n'))

    def _get_query_url(self):
        javascript = self.css('script').first.text
        url = re.search(r"\)\.autocomplete\([^']*'([^']*)'",
                        javascript).group(1)
        return url

    def _resolve_objects_to_path(self, values):
        new_values = []
        for value in values:
            if hasattr(value, 'getPhysicalPath'):
                new_values.append('/'.join(value.getPhysicalPath()))
            else:
                new_values.append(value)
        return new_values


@widget
class PatternsLibAutocompleteWidget(PloneWidget):
    """Represents the Autocomplete widget implemented with patternslib"""

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        return len(node.css('[data-pat-relateditems]')) > 0

    def fill(self, values):
        """With patternslib the Relation fields are represented as
        input text field containing one uid, or multiple uids seperated
        by a colon.
        """
        if not isinstance(values, (list, set, tuple)):
            values = [values]

        values = self._resolve_objects_to_uid(values)
        self.css('input').first.value = ':'.join(values)

    def _resolve_objects_to_uid(self, values):
        new_values = []
        for value in values:
            if hasattr(value, 'getPhysicalPath'):
                new_values.append(IUUID(value))
            else:
                new_values.append(value)
        return new_values
