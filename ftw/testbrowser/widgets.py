from ftw.testbrowser.nodes import NodeWrapper
from lxml import etree


WIDGETS = []


def widget(klass):
    WIDGETS.insert(0, klass)
    return klass


@widget
class PloneWidget(NodeWrapper):
    """Represents a Plone widget (div.field).
    """

    @staticmethod
    def match(node):
        return node.tag == 'div' and 'field' in node.classes

    def fill(self, value):
        """Subclassing widgets should implement this method or provide a name
        property for form filling to work.

        :param value: value to fill the widget inputs with.
        """
        raise NotImplementedError(
            '%s.%s does not implement fill(self, value)' % (
                self.__class__.__module__, self.__class__.__name__))

    @property
    def label(self):
        """Returns the label node of this widget.
        """
        return self.css('>label').first

    @property
    def fieldname(self):
        """The field name of the widget.
        """
        if self.attrib.get('data-fieldname', None) is not None:
            return self.attrib['data-fieldname']

        for cls in self.classes:
            if cls.startswith('kssattr-fieldname-'):
                return cls.split('kssattr-fieldname-', 1)[1]

        return None


@widget
class SequenceWidget(PloneWidget):
    """Represents a sequence widget, e.g. CheckBoxFieldWidget or
    RadioFieldWidget.
    """

    @staticmethod
    def match(node):
        if not node.tag == 'div' or not 'field' in node.classes:
            return False

        if len(node.css('span.option')) == 0:
            return False

        inputs = node.css('span.option input')
        if len(inputs) == 0:
            return False

        input_types = tuple(set([input.attrib.get('type', None)
                                 for input in inputs]))
        if input_types not in (('checkbox', ), ('radio', )):
            return False

        return True

    @property
    def options(self):
        """Available option labels.

        :returns: All available option labels.
        :rtype: list of string
        """
        options = []
        for label in self.css('span.option label'):
            options.append(label.normalized_text())
        return options

    @property
    def inputs(self):
        """Returns all inputs of this widget.

        :returns: <input> fields of this widgets.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.css('span.option input')

    @property
    def name(self):
        """Returns the name of the field.
        This allows the default mechanism to take place for filling the form.
        """
        return self.inputs.first.attrib['name']


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


@widget
class DateTimeWidget(PloneWidget):
    """Represents the z3cform datetime widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        name = PloneWidget(node).fieldname
        if not name:
            return False

        return len(node.css('input[name="%s-day"]' % name)) > 0

    def fill(self, value):
        """Fill the widget fields with a datetime object.

        :param value: datetime object for filling the fields.
        :type value: :py:class:`datetime.datetime`
        """
        name = self.fieldname

        self.css('*[name="%s-day"]' % name).first.set('value', str(value.day))
        self.css('*[name="%s-month"]' % name).first.value = str(value.month)
        self.css('*[name="%s-year"]' % name).first.set(
            'value', str(value.year))

        if self.css('*[name="%s-hour"]' % name):
            self.css('*[name="%s-hour"]' % name).first.set(
                'value', str(value.hour))
            self.css('*[name="%s-min"]' % name).first.set(
                'value', str(value.minute))
