from zope.publisher.browser import BrowserView
import json


class TestFormResult(BrowserView):

    def __call__(self):
        return json.dumps(self.request.form)
