from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class FileWidget(PloneWidget):
    """Represents an Archetypes file widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False
        return 'ArchetypesFileWidget' in node.classes

    def fill(self, value):
        field = self.css('input[type="file"]').first
        field.set('value', value)
