from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
import json


@widget
class AjaxSelectWidget(PloneWidget):
    """Represents the ajax select widget.
    """

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False
        return len(node.css('.pat-select2')) > 0

    def fill(self, values):
        if not isinstance(values, (list, set, tuple)):
            values = [values]

        separator = self.pat_data()['separator']
        self.css('input.pat-select2')[0].value = separator.join(values)

    def query(self, query_string):
        vocabulary_url = self.pat_data()['vocabularyUrl']
        with self.browser.clone() as query_browser:
            query_browser.open(vocabulary_url, data={'query': query_string})
            return [
                [item[u'id'], item[u'text']]
                for item in query_browser.json[u'results']
            ]

    def pat_data(self):
        return json.loads(
            self.css('input.pat-select2')[0].node.attrib['data-pat-select2'])
