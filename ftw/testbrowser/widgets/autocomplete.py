from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
from lxml import etree


@widget
class AutocompleteWidget(PloneWidget):
    """Represents the autocomplete widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        return len(node.css('div.autocompleteInputWidget')) > 0

    def fill(self, values):
        """Fill the autocomplete value with a key from the vocabulary.

        :param values: value to fill the autocomplete field with.
        :type values: string
        """
        if not isinstance(values, (list, set, tuple)):
            values = [values]

        container = self.css('div.autocompleteInputWidget').first
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

        from ftw.testbrowser import Browser
        from ftw.testbrowser import browser

        url = '/'.join((browser.url,
                        '++widget++%s' % self.fieldname,
                        '@@autocomplete-search'))

        with Browser()(browser.app) as query_browser:
            if browser._authentication:
                query_browser.login(*browser._authentication)

            query_browser.open(url, data={'q': query_string})
            return map(lambda line: line.split('|'),
                       query_browser.contents.split('\n'))
