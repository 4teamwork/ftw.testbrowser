from __future__ import absolute_import
from copy import deepcopy
from ftw.testbrowser.drivers.utils import isolated
from ftw.testbrowser.drivers.utils import remembering_for_reload
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import RedirectLoopException
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.utils import copy_docs_from_interface
from webtest import TestApp
from zope.interface import implementer
from ZPublisher.WSGIPublisher import publish_module
from ZPublisher.WSGIPublisher import set_default_debug_exceptions
import six


@isolated
def wsgi_app(environ, start_response):
    return publish_module(environ, start_response)


@copy_docs_from_interface
@implementer(IDriver)
class WebtestDriver(object):

    LIBRARY_NAME = 'webtest library'
    WEBDAV_SUPPORT = True

    def __init__(self, browser):
        self.browser = browser
        self.app = TestApp(wsgi_app)
        self.max_redirects = 5
        self.reset()

    def reset(self):
        self.response = None
        self.current_url = None
        self.headers = {}
        self.num_redirects = 0
        self.previous_make_request = None
        self.app.reset()

    @remembering_for_reload
    def make_request(self, method, url, data=None, headers=None,
                     referer_url=None):
        self.current_url = url
        headers = headers or {}

        if referer_url and referer_url.strip():
            headers['REFERER'] = referer_url

        headers.update(self.headers)

        if self.browser.exception_bubbling:
            set_default_debug_exceptions(True)
        else:
            set_default_debug_exceptions(False)

        if method.upper() == 'GET':
            self.response = self.app.get(
                url, params=data, headers=headers, expect_errors=True)
        elif method.upper() in ['POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS',
                                'HEAD']:
            impl = getattr(self.app, method.lower())
            data = self._encode_data(data)
            self.response = impl(
                url, params=data or '', headers=headers, expect_errors=True)
        else:
            self.response = self.app.request(
                url, expect_errors=True, method=method)

        if (self.browser.allow_redirects
                and self.response.status_code // 100 == 3):
            return self.follow_redirect(
                method, url, data=data, headers=headers)
        return (
            self.response.status_code,
            self.response.status[4:],
            self.response.body,
        )

    def follow_redirect(self, method, url, data=None, headers=None,
                        referer_url=None):
        if self.num_redirects > self.max_redirects:
            raise RedirectLoopException(url)
        self.num_redirects += 1
        location = self.response.headers.get('Location')
        if self.response.status_code in [301, 302] and method == 'POST':
            method = 'GET'
            data = None
        elif self.response.status_code == 303 and method == 'HEAD':
            method = 'GET'

        return self.make_request(
            method, location, data=data, headers=headers,
            referer_url=referer_url)

    def reload(self):
        if self.previous_make_request is None:
            raise BlankPage('Cannot reload.')
        return self.previous_make_request()

    def get_response_body(self):
        if self.response is None:
            raise BlankPage()
        return self.response.body

    def get_url(self):
        return self.current_url

    def get_response_headers(self):
        return self.response.headers

    def get_response_cookies(self):
        cookies = {}
        for cookie in self.app.cookiejar:
            cookies[cookie.name] = vars(cookie)
        return cookies

    def append_request_header(self, name, value):
        self.headers[name] = value

    def clear_request_header(self, name):
        if name in self.headers:
            del self.headers[name]

    def cloned(self, subbrowser):
        subdriver = subbrowser.get_driver(self.LIBRARY_NAME)
        subdriver.app.cookiejar._cookies = deepcopy(
            self.app.cookiejar._cookies)

    def _encode_data(self, data, charset='utf8'):
        if isinstance(data, dict) or hasattr(data, 'items'):
            data = list(data.items())
        if isinstance(data, (list, tuple)):
            encoded_data = []
            for k, v in data:
                if isinstance(v, six.text_type):
                    k = k.encode(charset)
                    v = v.encode(charset)
                encoded_data.append((k, v))
            return encoded_data
        return data
