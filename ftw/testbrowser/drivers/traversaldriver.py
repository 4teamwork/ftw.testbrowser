"""
TRAVERSAL DRIVER

GOAL:
The advantage of the traversal driver is that it executes requests within the
same Zope transaction and ZODB connection as the test is executed.
This makes it possible to no longer commit any transactions in tests, so that
the testbrowser can be used with Plone's IntegrationTesting layer.

BACKGROUND:
In projects which also use SQL / SQLAlchemy, it is hard to provide a testing
fixture with SQL data while still providing isolation between tests.
The reason is that it is hard to rollback any number of transactions in SQL,
as it is supported by the ZODB demo storage.
By stopping to commit we can isolate by rolling back transaction savepoints.

IMPLEMENTATION:
The traversal driver works quite a lot like Mechanize is set up internally
by plone.app.testing: it calls ``publish_module`` at the end.

For the session handling (cookies, authorization headers) and the request
preparation we use the ``requests`` module.
"""


from Acquisition import aq_base
from ftw.testbrowser.drivers.utils import isolated
from ftw.testbrowser.drivers.utils import remembering_for_reload
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import RedirectLoopException
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.utils import copy_docs_from_interface
from requests.structures import CaseInsensitiveDict
from StringIO import StringIO
from urllib import unquote
from urlparse import urlparse
from zope.interface import implements
from ZPublisher.BaseRequest import RequestContainer
from ZPublisher.Iterators import IStreamIterator
from ZPublisher.Response import Response
from ZPublisher.Test import publish_module
import httplib
import requests
import sys
import Zope2
import ZPublisher


# from plone.testing._z2_testbrowser
class TestResponse(Response):

    def setBody(self, body, title='', is_error=0, **kw):
        if IStreamIterator.providedBy(body):
            body = ''.join(body)
        Response.setBody(self, body, title, is_error, **kw)


class NoCommitTransactionsManagerWrapper(object):
    """
    On startup, Zope creates a ``ZApplicationWrapper`` instance and stores it
    as module global in the ``Zope2`` module.
    Whenever a request is processed with ``publish_module``, the application
    wrapper instance is injected as
    ``request['PARENTS'] = [application_wrapper]``
    and is therefore always bobo-traversed first when the traversal is started.
    Whenever the application wrapper is bobo-traversed, it opens a ZODB
    connection and gets the application root on this fresh connection.
    In order to reuse the testing connection in the request we want to prevent
    a ZODB connection to be opened.

    In ``publish_module``, the only thing happening between setting the
    application wrapper as ``PARENTS`` and traversing the path is that the
    transactions manager's ``begin()`` method is called.
    This is the reason we why we patch the transactions manager with this
    NoCommitTransactionsManagerWrapper in order to replace the ``PARENTS`` list
    to contain the actual application root so that no new ZODB connection is
    opened.

    Since the traversal driver should not reset or commit the transaction,
    we intercept those intents in the ``NoCommitTransactionsManagerWrapper``.
    Since we should only do that while processing a request, the wrapper is
    context manager which delegates to the original transactions manager when
    not active.
    """

    @classmethod
    def setup(klass):
        """Makes sure that the transactions manager is wrapped and the patch
        is installed.
        """
        if not isinstance(Zope2.zpublisher_transactions_manager, klass):
            # Patch the module global, from where ``get_module_info`` will
            # get the transactions manager.
            Zope2.zpublisher_transactions_manager = klass(
                Zope2.zpublisher_transactions_manager)

            # ``get_module_info`` caches the results in tis module cache.
            # The cache may already contain the module infos of Zope2.
            # By popping the caches of the Zope2 module it will be refeched
            # from Zope2.zpublisher_transactions_manager on the next call.
            modules_cache = ZPublisher.Publish.get_module_info.func_defaults[0]
            assert isinstance(modules_cache, dict), \
                'get_module_info modules cache changed unexpectedly.'
            modules_cache.pop('Zope2', None)
            modules_cache.pop('Zope2.cgi', None)

        return Zope2.zpublisher_transactions_manager

    def __init__(self, wrapped):
        self.wrapped = wrapped
        self.active = False
        self.next_request = None
        self.app = None

    def __call__(self, next_request, app):
        """Before the context manager is activated in the with-statement, it must
        be called for configuration.

        :param next_request: The request object which will be processed within
          this context manager next.
        :type next_request: :py:class:`ZPublisher.Request.Request`
        :param app: A zope application object from the current connection.
        :type app: Zope application object
        :returns: self
        :rtype: :py:class:`.NoCommitTransactionsManagerWrapper'
        """
        self.next_request = next_request
        self.app = app
        return self

    def __enter__(self):
        """While the context manager is active, all transaction interaction
        intents (begin, commit, abort, recordMetaData) will be silently
        ignored.
        """
        assert self.next_request is not None, (
            '{!r} must be called before'' activated with'
            ' "with"-statement'.format(self))
        self.active = True

    def __exit__(self, exc_type, exc_value, traceback):
        self.active = False
        self.next_request = None
        self.app = None

    def begin(self):
        if not self.active:
            return self.wrapped.begin()
        else:
            self.replace_app_in_parents()

    def commit(self):
        if not self.active:
            return self.wrapped.commit()

    def abort(self):
        if not self.active:
            return self.wrapped.abort()

    def recordMetaData(self, object, request):
        if not self.active:
            return self.wrapped.recordMetaData(object, request)

    def replace_app_in_parents(self):
        """When the ``ZApplicationWrapper`` is in the ``PARENTS`` list,
        it will make a new DB connection when bobo-traversed, which will
        not include the uncommitted state of the current transaction.
        With the NoCommitTransactionsManagerWrapper we make sure that this
        does not happen so that we have access to the uncommitted state in
        the request.
        """

        self.next_request['PARENTS'][0] = self.app


@copy_docs_from_interface
class TraversalDriver(object):
    """The traversal driver simulates requests by by calling
    the zope traversal directly.
    The purpose of the traversal driver is to be able to use a testbrowser
    in the same transaction / connection as the test code is run.
    This makes it possible to write browser tests without transactions.
    """
    implements(IDriver)

    LIBRARY_NAME = 'traversal library'
    WEBDAV_SUPPORT = True

    def __init__(self, browser):
        self.browser = browser
        self.reset()
        self.transactions_manager = NoCommitTransactionsManagerWrapper.setup()

    def reset(self):
        self.response = None
        self.current_url = None
        self.previous_make_request = None
        self.requests_session = requests.Session()
        self.append_request_header('X-zope-handle-errors', 'False')

    @remembering_for_reload
    @isolated
    def make_request(self, method, url, data=None, headers=None,
                     referer_url=None):
        if headers is None:
            headers = {}

        # The prepared_request is from the requests library and will be used
        # for extracting the cookies later. It is not used while publishing.
        # The zope_request is used for publishing.
        prepared_request, zope_request, response = self._prepare_for_request(
            method=method,
            url=url,
            data=data,
            headers=headers,
            referer_url=referer_url)

        # RequestContainer / Request Acquisition:
        # Views may get the request object through acquisition, for instance
        # by calling ``context.REQUEST``.
        # This works because the application object is acquisition wrapped
        # with a ``RequestContainer`` instance, which has a pointer to the
        # current request object.
        # Since we need to make sure that this is the request constructed
        # by the traversal driver, we need to unwrap the application and rewrap
        # it with a new ``RequestContainer`` instance.
        # If we would not do that views would end up with the test request.
        requestcontainer = RequestContainer(REQUEST=zope_request)
        app = aq_base(self.browser.app).__of__(requestcontainer)

        with self.transactions_manager(zope_request, app):
            try:
                publish_module(
                    'Zope2',
                    response=response,
                    request=zope_request,
                    debug=self.browser.exception_bubbling)

            except:
                self.response = None
                self.current_url = None
                raise

        self._extract_cookies(prepared_request, response)
        self.response = response
        self.current_url = prepared_request.url

        if self.response.status in (301, 302, 303):
            return self._follow_redirects(method, data, headers)
        else:
            return (self.response.status,
                    self.response.errmsg,
                    StringIO(self.response.body))

    def _prepare_for_request(self, method, url, data, headers, referer_url):
        if referer_url:
            headers['REFERER'] = referer_url.strip()
            headers['HTTP_REFERER'] = referer_url.strip()
        else:
            headers['REFERER'] = ''
            headers['HTTP_REFERER'] = ''

        # Use the requests library for creating a request because it can make
        # the body string for us (e.g. multipart MIME bodies).
        request = self.requests_session.prepare_request(
            requests.models.Request(
                method=method,
                url=url,
                data=data,
                headers=headers))

        urlinfo = urlparse(request.url)
        env = {
            'ACTUAL_URL': request.url,
            'HTTP_HOST': urlinfo.hostname,
            'PATH_INFO': unquote(urlinfo.path),
            'PATH_TRANSLATED': urlinfo.path,
            'QUERY_STRING': urlinfo.query,
            'REQUEST_METHOD': request.method,
            'SERVER_NAME': urlinfo.hostname,
            'SERVER_PORT': str(urlinfo.port or 80),
        }

        for name, value in request.headers.items():
            name = ('_'.join(name.upper().split('-')))
            if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                name = 'HTTP_' + name

            env[name] = value.rstrip()

        env['HTTP_CONNECTION'] = 'close'
        env['HTTP_USER_AGENT'] = 'ftw.testbrowser/traversaldriver'

        response = TestResponse(stdout=StringIO(), stderr=sys.stderr)

        # craft a new zope request
        zrequest = ZPublisher.Request.Request(
            stdin=StringIO(request.body or ''),
            environ=env,
            response=response)

        return request, zrequest, response

    def _extract_cookies(self, request, response):
        """Extract the cookies from the response into the current
        requests session.

        :param request: requests library request object
        :type request: :py:class:`requests.models.PreparedRequest`
        :param response: our drivers own testresponse
        :type response:
          :py:class:`ftw.testbrowser.drivers.traversaldriver.TestResponse`
        """
        # inspired by requests.cookies.extract_cookies_to_jar

        # Prepare the request object for cookielib compatibility:
        req = requests.cookies.MockRequest(request)

        # Prepare the response object for cookielib compatibility:
        res = requests.cookies.MockResponse(
            httplib.HTTPMessage(StringIO(response.stdout.getvalue())))

        self.requests_session.cookies.extract_cookies(res, req)

    def _follow_redirects(self, method, data, headers):
        redirect_url = self.get_response_headers().get('Location')
        if headers.get('X-Testbrowser-Last-Redirect-Location') == redirect_url:
            raise RedirectLoopException(redirect_url)
        else:
            headers['X-Testbrowser-Last-Redirect-Location'] = redirect_url

        # https://stackoverflow.com/a/8138447
        if (self.response.status == 303 and method.lower != 'head') or \
           (self.response.status == 301 and method.lower() == 'post') or \
           (self.response.status == 302 and method.lower() == 'post'):
            redirect_method = 'GET'
            redirect_data = None
        else:
            redirect_method = method
            redirect_data = data

        return self.make_request(method=redirect_method,
                                 url=redirect_url,
                                 data=redirect_data,
                                 headers=headers.copy(),
                                 referer_url=self.current_url)

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
        if self.response is None:
            return {}
        return CaseInsensitiveDict(self.response.headers)

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
