from zope.publisher.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
import json


class TestFormResult(BrowserView):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(self.request.form)


class TestStatusMessages(BrowserView):

    def __call__(self):
        messages = IStatusMessage(self.request)

        type_ = self.request.form.get('type', None)

        if type_ in ('info', None):
            messages.add('An info message.', 'info')

        if type_ in ('warning', None):
            messages.add('A warning message.', 'warning')

        if type_ in ('error', None):
            messages.add('An error message.', 'error')

        return self.request.response.redirect(self.context.portal_url())


class TestDumpRequest(BrowserView):

    def __call__(self):
        request_headers = [(name[len('HTTP_'):], value)
                           for (name, value) in self.request.environ.items()
                           if name.startswith('HTTP_')]

        result = {'HEADERS': dict(request_headers),
                  'METHOD': self.request.get('REQUEST_METHOD'),
                  'PATH_INFO': self.request.get('PATH_INFO'),
                  'QUERY_STRING': self.request.get('QUERY_STRING'),
                  'FORM': self.request.form}

        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(result)
