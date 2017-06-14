from ftw.testbrowser.drivers.utils import isolated
from ftw.testbrowser.drivers.utils import remembering_for_reload
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.exceptions import RedirectLoopException
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.utils import copy_docs_from_interface
from mechanize import Request
from mechanize._urllib2_fork import HTTPRedirectHandler
from requests.structures import CaseInsensitiveDict
from zope.interface import implements
import pkg_resources
import urllib
import urllib2


try:
    pkg_resources.get_distribution('zope.testbrowser')
except pkg_resources.DistributionNotFound:
    HAS_PLONE_EXTRAS = False
else:
    HAS_PLONE_EXTRAS = True
    from plone.testing._z2_testbrowser import Zope2MechanizeBrowser


@copy_docs_from_interface
class MechanizeDriver(object):
    """The mechanize driver uses the Mechanize browser with
    plone.testing integration for making the requests.
    """
    implements(IDriver)

    LIBRARY_NAME = 'mechanize library'
    WEBDAV_SUPPORT = False

    def __init__(self, browser):
        self.browser = browser
        self.reset()

    def reset(self):
        self.response = None
        self.mechbrowser = None
        self.previous_make_request = None

    @remembering_for_reload
    @isolated
    def make_request(self, method, url, data=None, headers=None,
                     referer_url=None):
        data = self._prepare_post_data(data)
        request = Request(url, data)
        if referer_url:
            self._add_headers_to_request(request,
                                         {'REFERER': referer_url,
                                          'HTTP_REFERER': referer_url})

        if self.browser.exception_bubbling:
            self._add_headers_to_request(
                request, {'X-zope-handle-errors': 'False'})

        self._add_headers_to_request(request, headers)

        try:
            self.response = self._get_mechbrowser().open(request)
        except urllib2.HTTPError as response:
            if response.reason.startswith(HTTPRedirectHandler.inf_msg):
                raise RedirectLoopException(response.geturl())

            self.response = response
        except:
            self.response = None
            raise

        return self.response.code, self.response.msg, self.response

    def reload(self):
        if self.previous_make_request is None:
            raise BlankPage('Cannot reload.')
        return self.previous_make_request()

    def get_response_body(self):
        if self.response is None:
            raise BlankPage()

        self.response.seek(0)
        return self.response.read()

    def get_url(self):
        if self.response is None:
            return None
        return self._get_mechbrowser().geturl()

    def get_response_headers(self):
        if getattr(self.response, 'info', None) is not None:
            return CaseInsensitiveDict(self.response.info().items())
        else:
            return {}

    def get_response_cookies(self):
        cookies = {}
        cookiejar = self._get_mechbrowser()._ua_handlers["_cookies"].cookiejar
        for cookie in cookiejar:
            cookies[cookie.name] = vars(cookie)
        return cookies

    def append_request_header(self, name, value):
        try:
            self._get_mechbrowser().addheaders.append((name, value))
        except BrowserNotSetUpException:
            pass

    def clear_request_header(self, name):
        try:
            addheaders = self._get_mechbrowser().addheaders
        except BrowserNotSetUpException:
            pass
        else:
            for header_name, value in addheaders[:]:
                if header_name == name:
                    addheaders.remove((header_name, value))

    def cloned(self, subbrowser):
        subdriver = subbrowser.get_driver(self.LIBRARY_NAME)
        subdriver._get_mechbrowser().set_cookiejar(
            self._get_mechbrowser()._ua_handlers['_cookies'].cookiejar)

    def _get_mechbrowser(self):
        if not HAS_PLONE_EXTRAS:
            raise ImportError(
                'Could not import zope.testbrowser.'
                ' Please install ftw.testbrowser[plone] extras.')

        if self.browser.app is None:
            raise BrowserNotSetUpException()

        if self.mechbrowser is None:
            self.mechbrowser = Zope2MechanizeBrowser(self.browser.app)
        return self.mechbrowser

    def _prepare_post_data(self, data):
        if not data:
            return None

        if isinstance(data, (str, unicode)):
            # We already have a payload, e.g. a MIME request.
            return data

        if isinstance(data, dict):
            data = data.items()

        normalized_data = []
        for name, value_or_values in data:
            if isinstance(name, unicode):
                name = name.encode('utf-8')

            if isinstance(value_or_values, (list, tuple, set)):
                values = value_or_values
            else:
                values = [value_or_values]

            for value in values:
                if isinstance(value, unicode):
                    value = value.encode('utf-8')

                normalized_data.append((name, value))

        return urllib.urlencode(normalized_data)

    def _add_headers_to_request(self, request, headers):
        if headers is None:
            return

        if isinstance(headers, dict):
            headers = headers.items()

        for key, val in headers:
            add_hdr = request.add_header
            if key.lower() == "content-type":
                try:
                    add_hdr = request.add_unredirected_header
                except AttributeError:
                    # pre-2.4 and not using ClientCookie
                    pass

            add_hdr(key, val)
