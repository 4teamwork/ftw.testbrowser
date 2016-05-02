from ftw.testbrowser.exceptions import OptionsNotFound
from ftw.testbrowser.utils import normalize_spaces
from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class ATMultiSelectionWidget(PloneWidget):
    """Represents an archetypes mutli selection widget.
    """

    @staticmethod
    def match(node):
        if not node.tag == 'div' or 'field' not in node.classes:
            return False

        inputs = node.css('div.ArchetypesMultiSelectionValue input')
        if len(inputs) == 0:
            return False

        input_types = tuple(set([input.attrib.get('type', None)
                                 for input in inputs]))
        if input_types != ('checkbox',):
            return False

        return True

    def fill(self, values):
        """Fill the widget inputs with the values passed as arguments.

        :param values: a list of names and / or labels of the options
        :type values: list of string
        """
        if not isinstance(values, (list, tuple, set)):
            values = [values]

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
            raise OptionsNotFound(normalize_spaces(self.label.raw_text),
                                  values, available_options)

    @property
    def label(self):
        """Returns the label node of this widget.

        :returns: Label node of this widget
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """
        return self.css('div.label').first

    @property
    def inputs(self):
        """Returns all inputs of this widget.

        :returns: <input> fields of this widgets.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.css('div.ArchetypesMultiSelectionValue input')

    @property
    def options(self):
        """Returns the option labels in order of occurence.

        :returns: Option labels
        :rtype: list of strings
        """

        result = []
        for input in self.inputs:
            if 'value' not in input.attrib:
                continue

            label = self.find_label_for_input(input)
            if not label:
                continue

            result.append(label.text)

        return result

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

            result[input.attrib['value']] = label.text

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
