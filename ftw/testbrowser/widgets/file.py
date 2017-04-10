from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class ArchetypesFileWidget(PloneWidget):
    """Represents an Archetypes file widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False
        return ('ArchetypesFileWidget' in node.classes or
                'ArchetypesImageWidget' in node.classes)

    def fill(self, value):
        field = self.css('input[type="file"]').first
        field.set('value', value)


@widget
class DexterityFileWidget(PloneWidget):
    """Represents a Dexterity namedfile widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False
        return (len(node.css('.named-file-widget')) > 0 or
                len(node.css('.named-image-widget')) > 0)

    def fill(self, value):
        field = self.css('input[type="file"]').first
        field.set('value', value)
