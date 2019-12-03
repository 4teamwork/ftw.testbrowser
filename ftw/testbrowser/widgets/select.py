from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget
from plone.uuid.interfaces import IUUID
from six.moves.urllib.parse import quote_plus

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


@widget
class RelatedItemsWidget(PloneWidget):
    """Represents the related items widget implemented with patternslib"""

    @staticmethod
    def match(node):
        if not PloneWidget.match(node):
            return False

        return len(node.css('.pat-relateditems')) > 0

    def fill(self, values):
        """With patternslib the Relation fields are represented as
        input text field containing one uid, or multiple uids seperated
        by a colon.
        """
        if not isinstance(values, (list, set, tuple)):
            values = [values]

        values = self._resolve_objects_to_uid(values)

        separator = self.pat_data()['separator']
        self.css('input').first.value = separator.join(values)

    def query(self, query_string):
        vocabulary_url = self.pat_data()['vocabularyUrl']
        query = {
            "criteria": [
                {
                    "i": "SearchableText",
                    "o": "plone.app.querystring.operation.string.contains",
                    "v": "*" + query_string + "*",
                },
            ],
        }
        attributes = [
            "UID", "Title", "portal_type", "path", "getURL", "getIcon",
            "is_folderish", "review_state",
        ]
        qs = '?query={}&attributes={}'.format(
            quote_plus(json.dumps(query, separators=(',', ':')), '*'),
            quote_plus(json.dumps(attributes, separators=(',', ':')), '*'),
        )
        with self.browser.clone() as query_browser:
            query_browser.open(vocabulary_url + qs)
            return [
                [item[u'UID'], item[u'Title']]
                for item in query_browser.json[u'results']
            ]

    def _resolve_objects_to_uid(self, values):
        new_values = []
        for value in values:
            if hasattr(value, 'getPhysicalPath'):
                new_values.append(IUUID(value))
            else:
                new_values.append(value)
        return new_values

    def pat_data(self):
        return json.loads(self.css(
            'input.pat-relateditems')[0].node.attrib['data-pat-relateditems'])
