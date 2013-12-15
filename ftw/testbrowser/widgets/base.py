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
