from zope.publisher.browser import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
import json


class TestFormResult(BrowserView):

    def __call__(self):
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
