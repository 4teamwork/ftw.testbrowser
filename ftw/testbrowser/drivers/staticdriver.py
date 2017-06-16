from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.utils import copy_docs_from_interface
from zope.interface import implements


@copy_docs_from_interface
class StaticDriver(object):
    """The static driver can load static HTML without doing an actual request.
    It does not support making requests at all.
    """
    implements(IDriver)

    LIBRARY_NAME = 'static driver'
    WEBDAV_SUPPORT = False

    def __init__(self, browser):
        self.browser = browser
        self.reset()

    def reset(self):
        self.body = None

    def set_body(self, body):
        self.body = body

    def make_request(self, method, url, data=None, headers=None,
                     referer_url=None):
        raise NotImplementedError(
            'The StaticDriver does not support making requests.')

    def reload(self):
        if self.body is None:
            raise BlankPage('Cannot reload.')
        return 200, 'OK', self.body

    def get_response_body(self):
        if self.body is None:
            raise BlankPage()
        return self.body

    def get_url(self):
        return None

    def get_response_headers(self):
        return {}

    def get_response_cookies(self):
        return {}

    def append_request_header(self, name, value):
        pass

    def clear_request_header(self, name):
        pass

    def cloned(self, subbrowser):
        pass
