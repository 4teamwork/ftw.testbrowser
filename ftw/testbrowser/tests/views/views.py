from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zope.publisher.browser import BrowserView
import json
import os.path


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


class TestAsset(BrowserView):

    asset_encodings = {'cities-utf8.xml': 'utf-8',
                       'cities-iso-8859-1.xml': 'ISO-8859-1'}

    def __call__(self):
        filename = self.request.get('filename')
        if not filename:
            raise BadRequest('"filename" missing')

        assets = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '..', 'assets'))

        path = os.path.join(assets, filename.replace('/', '_'))
        if not os.path.exists(path):
            raise ValueError('No such file: "{0}"'.format(path))


        mimetypes_registry = getToolByName(self.context, 'mimetypes_registry')
        with open(path, 'rb') as file_:
            mimetype = str(mimetypes_registry.classify(file_.read(), filename=filename))

        encoding = self.asset_encodings.get(filename)

        if encoding:
            self.request.response.setHeader('Content-Type', '{0}; charset={1}'.format(
                    mimetype, encoding))
        else:
            self.request.response.setHeader('Content-Type', mimetype)

        with open(path, 'rb') as file_:
            return file_.read()


class TestRedirectToPortal(BrowserView):

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return self.request.response.redirect(portal_url)


class TestRedirectLoop(BrowserView):

    def __call__(self):
        return self.request.response.redirect(self.request['ACTUAL_URL'])
