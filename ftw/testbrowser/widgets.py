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
        raise NotImplementedError('%s.%s does not implement fill(self, value)' % (
                self.__class__.__module__, self.__class__.__name__))

    @property
    def label(self):
        return self.css('>label').first


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
        options = []
        for label in self.css('span.option label'):
            options.append(label.normalized_text())
        return options

    @property
    def inputs(self):
        return self.css('span.option input')

    @property
    def name(self):
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
        if not isinstance(values, (list, set, tuple)):
            values = [values]

        container = self.css('div.autocompleteInputWidget').first
        fieldname = '%s:list' % self.attrib['data-fieldname']

        # remove currently selected values
        for span in container.css('span.option'):
            span.node.getparent().remove(span.node)

        # add new values
        for value in values:
            span = etree.SubElement(container.node, 'span', {'class': 'option'})
            etree.SubElement(span, 'input', {
                    'type': 'checkbox',
                    'name': fieldname,
                    'value': value,
                    'checked': 'checked'})
            etree.SubElement(span, 'label').text = value


@widget
class DateTimeWidget(PloneWidget):
    """Represents the z3cform datetime widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        name = node.attrib.get('data-fieldname', None)
        if not name:
            return False

        return len(node.css('input[name="%s-day"]' % name)) > 0

    def fill(self, value):
        name = self.attrib.get('data-fieldname')

        self.css('*[name="%s-day"]' % name).first.set('value', str(value.day))
        self.css('*[name="%s-month"]' % name).first.value = str(value.month)
        self.css('*[name="%s-year"]' % name).first.set('value', str(value.year))

        if self.css('*[name="%s-hour"]' % name):
            self.css('*[name="%s-hour"]' % name).first.set('value', str(value.hour))
            self.css('*[name="%s-min"]' % name).first.set('value', str(value.minute))
