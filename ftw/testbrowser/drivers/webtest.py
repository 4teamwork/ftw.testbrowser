from webtest import TestApp
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.utils import copy_docs_from_interface
from zope.interface import implementer
from ZPublisher.WSGIPublisher import publish_module
import ZPublisher.WSGIPublisher
from contextlib import contextmanager


class WSGIApp(object):

    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def __iter__(self):
        import pdb; pdb.set_trace()
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        self.start(status, response_headers)
        yield b"Hello world!\n"


def wsgi_app(environ, start_response):
    res = publish_module(environ, start_response)
    return res


class NoCommitTransactionsManager(object):

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.active = False

    def __enter__(self):
        """While the context manager is active, all transaction interaction
        intents (begin, commit, abort, recordMetaData) will be silently
        ignored.
        """
        self.active = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.active = False

    def begin(self):
        if not self.active:
            return self.wrapped.begin()

    def commit(self):
        import pdb; pdb.set_trace()
        if not self.active:
            return self.wrapped.commit()

    def abort(self):
        if not self.active:
            return self.wrapped.abort()

    def savepoint(self, optimistic=False):
        import pdb; pdb.set_trace()
        if not self.active:
            return self.wrapped.savepoint(optimistic=optimistic)

    def recordMetaData(self, object, request):
        if not self.active:
            return self.wrapped.recordMetaData(object, request)


APP = None


@contextmanager
def load_app(module_info):
    app_wrapper, realm, debug_mode = module_info
    app = APP
    yield (app, realm, debug_mode)


ZPublisher.WSGIPublisher.load_app = load_app


@copy_docs_from_interface
@implementer(IDriver)
class WebtestDriver(object):

    def __init__(self, browser):
        self.browser = browser
        self.app = TestApp(wsgi_app)
        self.reset()
        global APP
        APP = browser.app
        self.tm = NoCommitTransactionsManager(APP._p_jar.transaction_manager)
        APP._p_jar.transaction_manager = self.tm

    def reset(self):
        self.response = None
        self.current_url = None
        self.headers = {}
        self.no_redirects = 0

    def make_request(self, method, url, data=None, headers=None,
                     referer_url=None):
        self.current_url = url
        headers = headers or {}
        headers.update(self.headers)
        with self.tm:
            if method == 'GET':
                self.response = self.app.get(url, params=data, headers=headers)
            elif method == 'POST':
                self.response = self.app.post(url, params=data or '', headers=headers)
            if self.response.status_code // 100 == 3:
                return self.follow_redirect(method, url, data=data, headers=headers)
        return (
            self.response.status_code,
            self.response.status.split()[-1],
            self.response.body,
        )

    def follow_redirect(self, method, url, data=None, headers=None,
                        referer_url=None):
        if self.no_redirects > 10:
            raise ValueError('Max redirect exceeded')
        self.no_redirects += 1
        location = self.response.headers.get('Location')
        if self.response.status_code in [301, 302] and method == 'POST':
            method = 'GET'
            data = None
        elif self.response.status_code == 303 and method == 'HEAD':
            method = 'GET'

        return self.make_request(
            method, location, data=data, headers=headers, referer_url=referer_url)

    def reload(self):
        pass

    def get_response_body(self):
        return self.response.body

    def get_url(self):
        return self.current_url

    def get_response_headers(self):
        return self.response.headers

    def get_response_cookies(self):
        import pdb; pdb.set_trace()
        pass

    def append_request_header(self, name, value):
        self.headers[name] = value

    def clear_request_header(self, name):
        if name in self.headers:
            del self.headers[name]

    def cloned(self, subbrowser):
        pass
