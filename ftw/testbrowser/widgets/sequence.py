from ftw.testbrowser.exceptions import OnlyOneValueAllowed
from ftw.testbrowser.exceptions import OptionsNotFound
from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class SequenceWidget(PloneWidget):
    """Represents a sequence widget, e.g. CheckBoxFieldWidget or
    RadioFieldWidget.
    """

    @staticmethod
    def match(node):
        if not node.tag == 'div' or 'field' not in node.classes:
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
    def multiple(self):
        """Returns ``True`` when the widget allows multiple values (checkboxes)
        or ``False`` if only one value is allowed (radios).
        """
        input_types = set([input.attrib.get('type', None)
                           for input in self.inputs])
        return 'checkbox' in input_types

    def fill(self, values):
        """Fill the widget inputs with the values passed as arguments.

        :param values: a list of names and / or labels of the options
        :type values: list of string
        """
        if not isinstance(values, (list, tuple, set)):
            values = [values]

        if not self.multiple and len(values) > 1:
            raise OnlyOneValueAllowed()

        # deselect existing options
        for input in self.inputs:
            input.checked = False

        # normalize value labels to names
        reverse_option_map = dict(map(reversed, self.option_map.items()))
        values = [reverse_option_map.get(value, value) for value in values]

        # fill new values
        for input in self.inputs:
            if 'value' not in input.attrib:
                continue

            if input.attrib['value'] in values:
                input.checked = True
                values.remove(input.attrib['value'])

        if values:
            available_options = self.options
            raise OptionsNotFound(
                self.label.normalized_text(), values, available_options)

    @property
    def options(self):
        """Available option labels.

        :returns: All available option labels.
        :rtype: list of string
        """
        return sorted(self.inputs_by_label.keys())

    @property
    def option_map(self):
        """A dict with all available options, having the key as term token
        and the value as term label.

        :returns: Available options
        :rtype: dict
        """

        result = {}
        for input in self.inputs:
            if 'value' not in input.attrib:
                continue

            label = self.find_label_for_input(input)
            if not label:
                continue

            result[input.attrib['value']] = label.normalized_text()

        return result

    @property
    def inputs(self):
        """Returns all inputs of this widget.

        :returns: <input> fields of this widgets.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.css('span.option input')

    @property
    def inputs_by_value(self):
        """Returns a dict of input value to input node mapping.

        :returns: dict of inputs by value
        :rtype: dict
        """

        result = {}
        for input in self.inputs:
            if 'value' not in input.attrib:
                continue

            result[input.attrib['value']] = input

        return result

    @property
    def inputs_by_label(self):
        """Returns a dict of inputs where the key is the label of the input.

        :returns: dict of inputs by label
        :rtype: dict
        """

        result = {}
        for input in self.inputs:
            label = self.find_label_for_input(input)
            if not label:
                continue

            result[label.normalized_text()] = input

        return result

    def find_label_for_input(self, input):
        """Searches for the <label> node associated with the <input>
        node passed as argument and returns it.

        :returns: <label> node for the <input>
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        if 'id' in input.attrib:
            labels = self.xpath('//label[@for="%s"]' % input.attrib['id'])
            if labels:
                return labels.first

        if 'name' in input.attrib:
            labels = self.xpath('//label[@for="%s"]' % input.attrib['name'])
            if labels:
                return labels.first

        return None
