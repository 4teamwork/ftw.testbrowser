from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class Plone5TextWidget(PloneWidget):
    """Represents plone 5 text widget
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False
        textarea = node.css('>textarea')
        return textarea and 'pat-tinymce' in textarea.first.classes

    def fill(self, value):
        self.css('>textarea').first.text = value
