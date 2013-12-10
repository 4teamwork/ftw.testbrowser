from ftw.testbrowser.nodes import NodeWrapper

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
        raise NotImplementedError()

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
