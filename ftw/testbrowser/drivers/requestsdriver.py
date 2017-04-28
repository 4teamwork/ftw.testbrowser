from ftw.testbrowser.drivers.utils import remembering_for_reload
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import ZServerRequired
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.utils import copy_docs_from_interface
from ftw.testbrowser.utils import verbose_logging
from StringIO import StringIO
from zope.interface import implements
import requests
import urlparse


@copy_docs_from_interface
class RequestsDriver(object):
    """The requests driver uses the "requests" library for making
    real requests.
    """
    implements(IDriver)

    LIBRARY_NAME = 'requests library'

    def __init__(self, browser):
        self.browser = browser
        self.reset()

    def reset(self):
        self.response = None
        self.previous_make_request = None
        self.requests_session = requests.Session()

    @remembering_for_reload
    def make_request(self, method, url, data=None, headers=None,
                     referer_url=None):
        if urlparse.urlparse(url).hostname == 'nohost':
            raise ZServerRequired()

        if self.browser.exception_bubbling:
            raise ValueError('The requests driver does not support'
                             ' exception bubbling.')

        if headers is None:
            headers = {}

        if referer_url and referer_url.strip():
            headers['REFERER'] = referer_url
            headers['HTTP_REFERER'] = referer_url

        with verbose_logging():
            self.response = self.requests_session.request(
                method, url, data=data, headers=headers)

            return (self.response.status_code,
                    self.response.reason,
                    StringIO(self.response.content))

    def reload(self):
        if self.previous_make_request is None:
            raise BlankPage('Cannot reload.')
        return self.previous_make_request()

    def get_response_body(self):
        if self.response is None:
            raise BlankPage()
        return self.response.content

    def get_url(self):
        if self.response is None:
            return None
        return self.response.url

    def get_response_headers(self):
        if self.response is None:
            return {}
        return self.response.headers

    def get_response_cookies(self):
        cookies = {}
        cookiejar = self.requests_session.cookies
        for domain_cookies in cookiejar._cookies.values():
            for path_cookies in domain_cookies.values():
                for cookie_name, cookie in path_cookies.items():
                    cookies[cookie_name] = vars(cookie)
        return cookies

    def append_request_header(self, name, value):
        if name in self.requests_session.headers:
            raise NameError(
                ('There is already a header "{}" and the requests driver'
                 ' does not support using the same header multiple times.')
                .format(name))

        self.requests_session.headers.update({name: value.strip()})

    def clear_request_header(self, name):
        if name in self.requests_session.headers:
            del self.requests_session.headers[name]

    def cloned(self, subbrowser):
        subdriver = subbrowser.get_driver(self.LIBRARY_NAME)
        requests.cookies.merge_cookies(subdriver.requests_session.cookies,
                                       self.requests_session.cookies)
