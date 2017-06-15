from Acquisition import aq_chain
from contextlib import contextmanager
from copy import deepcopy
from ftw.testbrowser.drivers.mechdriver import MechanizeDriver
from ftw.testbrowser.drivers.requestsdriver import RequestsDriver
from ftw.testbrowser.drivers.staticdriver import StaticDriver
from ftw.testbrowser.drivers.traversaldriver import TraversalDriver
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.exceptions import ContextNotFound
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.exceptions import HTTPClientError
from ftw.testbrowser.exceptions import HTTPError
from ftw.testbrowser.exceptions import HTTPServerError
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.exceptions import NoWebDAVSupport
from ftw.testbrowser.interfaces import IBrowser
from ftw.testbrowser.log import ExceptionLogger
from ftw.testbrowser.nodes import wrap_nodes
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.utils import normalize_spaces
from ftw.testbrowser.utils import parse_html
from lxml.cssselect import CSSSelector
from OFS.interfaces import IItem
from operator import attrgetter
from operator import methodcaller
from StringIO import StringIO
from zope.component.hooks import getSite
from zope.interface import implements
import json
import lxml
import lxml.html
import os
import pkg_resources
import re
import tempfile
import urlparse


try:
    pkg_resources.get_distribution('plone.app.testing')
except pkg_resources.DistributionNotFound:
    TEST_USER_NAME = 'test-user'
    TEST_USER_PASSWORD = 'secret'
else:
    from plone.app.testing import TEST_USER_NAME
    from plone.app.testing import TEST_USER_PASSWORD


#: Constant for choosing the mechanize library (interally dispatched requests)
LIB_TRAVERSAL = TraversalDriver.LIBRARY_NAME

#: Constant for choosing the requests library (actual requests)
LIB_REQUESTS = RequestsDriver.LIBRARY_NAME

#: Constant for choosing the mechanize library (interally dispatched requests)
LIB_MECHANIZE = MechanizeDriver.LIBRARY_NAME

#: Constant for choosing the static driver.
LIB_STATIC = StaticDriver.LIBRARY_NAME


#: Mapping of driver library constants to its factories.
#: This design is historical so that the library constants
#: keep working. This mapping may be monkey patched.
DRIVER_FACTORIES = {
    TraversalDriver.LIBRARY_NAME: TraversalDriver,
    MechanizeDriver.LIBRARY_NAME: MechanizeDriver,
    RequestsDriver.LIBRARY_NAME: RequestsDriver,
    StaticDriver.LIBRARY_NAME: StaticDriver}


class Browser(object):
    """The ``Browser`` is the top level object of ``ftw.testbrowser``.
    It represents the browser instance and is used for navigating and
    interacting with the browser.

    The ``Browser`` is a context manager, requiring the Zope app to be set:

    .. code:: py

        # "app" is the Zope app object

        from ftw.testbrowser import Browser

        browser = Browser()

        with browser(app):
            browser.open()

    When using the browser in tests there is a ``@browsing`` test-method
    decorator uses the global (singleton) browser and sets it up / tears it
    down using the context manager syntax. See the
    `ftw.testbrowser.browsing`_ documentation for more information.

    :ivar raise_http_errors: HTTPError exceptions are raised on 4xx
      and 5xx response codes when enabled (Default: ``True``).
    :type raise_http_errors: ``bool``

    :ivar exception_bubbling: When enabled, exceptions from within the Zope
      view are bubbled up into the test method if the driver supports it.
      (Default: ``False``).
    :type exception_bubbling: ``bool``
    """

    implements(IBrowser)

    def __init__(self):
        self.drivers = {}
        self.default_driver = None
        self._log_exceptions = True
        self.reset()

    def __call__(self, app):
        """Calling the browser instance with the Zope app object as argument
        sets configures the Zope app to be used for the next session, which is
        initailized by using the context manager syntax.
        """
        self.next_app = app
        return self

    def __repr__(self):
        return '<ftw.browser.core.Browser instance>'

    def reset(self):
        """Resets the browser: closes active sessions and resets the internal
        state.
        """
        self.request_library = None
        self.raise_http_errors = True
        self.exception_bubbling = False
        self.next_app = None
        self.app = None
        self.document = None
        self.previous_url = None
        self.form_files = {}
        self.session_headers = []
        self._status_code = None
        self._status_reason = None
        map(methodcaller('reset'), self.drivers.values())

    def __enter__(self):
        if self.request_library is None:
            if self.default_driver is not None:
                self.request_library = self.default_driver
            elif self.next_app is None:
                self.request_library = LIB_REQUESTS
            else:
                self.request_library = LIB_MECHANIZE

        if self.app is None:
            self.app = self.next_app

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (exc_type or exc_value):
            try:
                source = self.contents
            except BlankPage:
                pass
            else:
                _, path = tempfile.mkstemp(suffix='.html',
                                           prefix='ftw.testbrowser-')
                with open(path, 'w+') as file_:
                    if isinstance(source, unicode):
                        source = source.encode('utf-8')

                    file_.write(source)

                print '\nftw.testbrowser dump:', path,

        self.reset()

    def get_driver(self, library=None):
        """Return the driver instance for a library.
        """
        if library is not None:
            self.request_library = library
        else:
            library = self.request_library

        if library not in self.drivers:
            self.drivers[library] = driver = DRIVER_FACTORIES[library](self)
            for header_name, header_value in self.session_headers:
                driver.clear_request_header(header_name)
                driver.append_request_header(header_name, header_value)

        return self.drivers[library]

    def open(self, url_or_object=None, data=None, view=None, library=None,
             referer=False, method=None, headers=None):
        """Opens a page in the browser.

        *Request library:*
        When running tests on a Plone testing layer and using the ``@browsing``
        decorator, the ``mechanize`` library is used by default, dispatching
        the request internal directly into Zope.
        When the testbrowser is used differently (no decorator nor zope app
        setup), the ``requests`` library is used, doing actual requests.
        If the default does not fit your needs you can change the library per
        request by passing in ``LIB_MECHANIZE`` or ``LIB_REQUESTS`` or you can
        change the library for the session by setting
        ``browser.request_library`` to either of those constants.

        :param url_or_object: A full qualified URL or a Plone object (which has
          an ``absolute_url`` method). Defaults to the Plone Site URL.
        :param data: A dict with data which is posted using a `POST` request,
          or request payload as string.
        :type data: dict or string
        :param view: The name of a view which will be added at the end of the
          current URL.
        :type view: string
        :param library: Lets you explicitly choose the request library to be
          used for this request.
        :type library: ``LIB_MECHANIZE`` or ``LIB_REQUESTS``
        :param referer: Sets the referer when set to ``True``.
        :type referer: Boolean (Default ``False``)
        :param method: The HTTP request method. Defaults to 'GET' when not set,
          unless ``data`` is provided, then its set to 'POST'.
        :type method: string
        :param headers: A dict with custom headers for this request.
        :type headers: dict

        .. seealso:: :py:func:`visit`
        .. seealso:: :py:const:`LIB_MECHANIZE`
        .. seealso:: :py:const:`LIB_REQUESTS`
        """
        self._verify_setup()
        self.previous_url = self.url
        library = library or self.request_library

        if method is None and data is None:
            method = 'GET'
        elif method is None:
            method = 'POST'

        if referer is True and self.url:
            referer_url = self.url
        else:
            referer_url = ' '

        url = self._normalize_url(url_or_object, view=view)
        driver = self.get_driver(library)
        with ExceptionLogger() as logger:
            self._status_code, self._status_reason, body = driver.make_request(
                method, url, data=data,
                referer_url=referer_url,
                headers=headers)

        self.parse(body)
        self.raise_for_status(logger)
        return self

    def raise_for_status(self, exception_logger):
        if self._log_exceptions:
            exception_logger.print_captured_exceptions()

        if not self.raise_http_errors:
            return

        if 400 <= self.status_code < 500:
            raise HTTPClientError(self.status_code, self.status_reason)
        elif 500 <= self.status_code < 600:
            raise HTTPServerError(self.status_code, self.status_reason)

    def on(self, url_or_object=None, data=None, view=None, library=None):
        """``on`` does almost the same thing as ``open``. The difference is that
        ``on`` does not reload the page if the current page is the same as the
        requested one.

        Be aware that filled form field values may stay when the page is
        not reloaded.

        .. seealso:: :py:func:`open`
        """
        url = self._normalize_url(url_or_object, view=view)
        if url == self.url:
            return self

        return self.open(url_or_object=url_or_object, data=data, view=view,
                         library=library)

    def open_html(self, html):
        """Opens a HTML page in the browser without doing a request.
        The passed ``html`` may be a string or a file-like stream.

        :param html: The HTML content to load in the browser.
        :type html: string or file-like object
        :returns: The browser object.
        """
        self.get_driver(LIB_STATIC).set_body(html)
        self.parse(html)
        self._status_code = 200
        self._status_reason = 'OK'
        return self

    def visit(self, *args, **kwargs):
        """Visit is an alias for :py:func:`open`.

        .. seealso:: :py:func:`open`
        """
        return self.open(*args, **kwargs)

    def webdav(self, method, url_or_object=None, data=None, view=None,
               headers=None):
        """Makes a webdav request to the Zope server.

        It is required that a ``ZSERVER_FIXTURE`` is used in the test setup
        (e.g. ``PLONE_ZSERVER'' from ``plone.app.testing``).

        :param method: The HTTP request method (``OPTIONS``, ``PROPFIND``, etc)
        :type method: string
        :param url_or_object: A full qualified URL or a Plone object (which has
        an ``absolute_url`` method). Defaults to the Plone Site URL.
        :param data: A dict with data which is posted using a `POST` request.
        :type data: dict
        :param view: The name of a view which will be added at the end of the
        current URL.
        :type view: string
        :param headers: Pass in reqest headers.
        :type headers: dict
        """
        self._verify_setup()
        url = self._normalize_url(url_or_object, view=view)
        driver = self.get_driver()
        if not driver.WEBDAV_SUPPORT:
            raise NoWebDAVSupport()

        self._status_code, self._status_reason, body = driver.make_request(
            method, url, data=data, headers=headers)
        self.parse(body)
        return self

    def reload(self):
        """Reloads the current page by redoing the previous requests with
        the same arguments.
        This applies for GET as well as POST requests.

        :raises: :py:exc:`ftw.testbrowser.exceptions.BlankPage`
        :returns: The browser object.
        :rtype: :py:class:`ftw.testbrowser.core.Browser`
        """
        self._verify_setup()
        driver = self.get_driver()

        with ExceptionLogger() as logger:
            self._status_code, self._status_reason, body = driver.reload()

        self.parse(body)
        self.raise_for_status(logger)
        return self

    @property
    def contents(self):
        """The source of the current page (usually HTML).
        """
        self._verify_setup()
        return self.get_driver().get_response_body()

    @property
    def json(self):
        """If the current page is JSON only, this can be used for getting the
        converted JSON data as python data structure.
        """
        return json.loads(self.contents)

    @property
    def status_code(self):
        """The status code of the last response or ``None`` when no request
        was done yet.

        :type: `int`
        """
        return self._status_code

    @property
    def status_reason(self):
        """The status reason of the last response or ``None`` when no request
        was done yet.
        Examples: ``"OK"``, ``"Not Found"``.

        :type: `string`
        """
        return self._status_reason

    @property
    def headers(self):
        """A dict of response headers.
        """
        return self.get_driver().get_response_headers()

    @property
    def contenttype(self):
        """The contenttype of the response, e.g. ``text/html; charset=utf-8``.

        .. seealso:: :py:func:`mimetype`, :py:func:`encoding`
        """
        return self.headers.get('Content-Type', '')

    @property
    def mimetype(self):
        """The mimetype of the respone, e.g. ``text/html``.

        .. seealso:: :py:func:`contenttype`
        """
        return self.contenttype.split(';', 1)[0]

    @property
    def encoding(self):
        """The encoding of the respone, e.g. ``utf-8``.

        .. seealso:: :py:func:`contenttype`
        """
        match = re.match(r'[^;]*; ?charset="?([^"]*)"?', self.contenttype)
        if match:
            return match.group(1)

    def append_request_header(self, name, value):
        """Add a new permanent request header which is sent with every request
        until it is cleared.

        HTTP allows multiple request headers with the same name.
        Therefore this method does not replace existing names.
        Use `replace_request_header` for replacing headers.

        Be aware that the ``requests`` library does not support multiple
        headers with the same name, therefore it is always a replace
        for the requests module.

        :param name: Name of the request header
        :type name: string
        :param value: Value of the request header
        :type value: string

        .. seealso:: :py:func:`replace_request_header`
        .. seealso:: :py:func:`clear_request_header`
        """

        if name.lower() == 'x-zope-handle-errors':
            raise ValueError(
                'The testbrowser does no longer allow to set the request'
                ' header \'X-zope-handle-errros\'; use the'
                ' exception_bubbling flag instead.'
            )

        self.session_headers.append((name, value))
        for driver in self.drivers.values():
            driver.append_request_header(name, value)

    def replace_request_header(self, name, value):
        """Adds a permanent request header which is sent with every request.
        Before adding the request header all existing request headers with the
        same name are removed.

        :param name: Name of the request header
        :type name: string
        :param value: Value of the request header
        :type value: string

        .. seealso:: :py:func:`replace_request_header`
        .. seealso:: :py:func:`clear_request_header`
        """

        self.clear_request_header(name)
        self.append_request_header(name, value)

    def clear_request_header(self, name):
        """Removes a permanent header.
        If there are no such headers, the removal is silently skipped.

        :param name: Name of the request header as positional arguments
        :type name: string
        """

        if name.lower() == 'x-zope-handle-errors':
            raise ValueError(
                'The testbrowser does no longer allow to set the request'
                ' header \'X-zope-handle-errros\'; use the'
                ' exception_bubbling flag instead.'
            )

        for header_name, value in self.session_headers[:]:
            if header_name == name:
                self.session_headers.remove((header_name, value))

        for driver in self.drivers.values():
            driver.clear_request_header(name)

    @property
    def cookies(self):
        """A read-only dict of current cookies.
        """

        return self.get_driver().get_response_cookies()

    @property
    def url(self):
        """The URL of the current page.
        """
        return self.get_driver().get_url()

    @property
    def base_url(self):
        """The base URL of the current page.
        The base URL can be defined in HTML using a ``<base>``-tag.
        If no ``<base>``-tag is found, the page URL is used.
        """
        base_tags = self.css('base')
        if base_tags:
            return base_tags.first.attrib.get('href', self.url)
        return self.url

    def login(self, username=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        """Login a user by setting the ``Authorization`` header.
        """

        if hasattr(username, 'getUserName'):
            username = username.getUserName()

        self.replace_request_header(
            'Authorization', 'Basic {0}'.format(
                ':'.join((username, password)).encode('base64').strip()))
        return self

    def logout(self):
        """Logout the current user by removing the ``Authorization`` header.
        """
        self.clear_request_header('Authorization')
        return self

    def css(self, css_selector):
        """Select one or more HTML nodes by using a *CSS* selector.

        :param css_selector: The CSS selector.
        :type css_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        query_info = ('browser', 'css', css_selector)
        return self.xpath(CSSSelector(css_selector).path,
                          query_info=query_info)

    def xpath(self, xpath_selector, query_info=None):
        """Select one or more HTML nodes by using an *xpath* selector.

        :param xpath_selector: The xpath selector.
        :type xpath_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        query_info = query_info or ('browser', 'xpath', xpath_selector)
        nsmap = self.document.getroot().nsmap
        return wrap_nodes(
            self.document.xpath(xpath_selector, namespaces=nsmap),
            self,
            query_info=query_info)

    @property
    @wrapped_nodes
    def root(self):
        """The current document root node.
        """
        return self.document.getroot()

    @property
    def forms(self):
        """A *dict* of form instance where the key is the `id` or the `name` of
        the form and the value is the form node.
        """
        forms = {}

        for index, node in enumerate(self.css('form')):
            key = node.attrib.get('id', node.attrib.get(
                'name', 'form-%s' % index))
            forms[key] = node

        return forms

    def fill(self, values):
        """Fill multiple fields of a form on the current page.
        All fields must be in the same form.

        Example:

        .. code:: py

            browser.open(view='login_form')
            browser.fill({'Login Name': 'hugo.boss', 'Password': 'secret'})

        Since the form node (:py:class:`ftw.testbrowser.form.Form`) is
        returned, it can easily be submitted:

        .. code:: py

            browser.open(view='login_form')
            browser.fill({'Login Name': 'hugo.boss',
                          'Password': 'secret'}).submit()

        :param values: The key is the label or input-name and the value is the
          value to set.
        :type values: dict
        :returns: The form node.
        :rtype: :py:class:`ftw.testbrowser.form.Form`
        """
        form = self.find_form_by_fields(*values.keys())
        return form.fill(values)

    def find(self, text, within=None):
        """Find an element by text.
        This will look for:

        - a link with this text (normalized, including subelements' texts)
        - a field which has a label with this text
        - a button which has a label with this text

        :param text: The text to be looked for.
        :type text: string
        :param within: A node object for limiting the scope of the search.
        :type within: :py:class:`ftw.testbrowser.nodes.NodeWrapper`.
        :returns: A single node object or `None` if nothing matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        link = self.find_link_by_text(text, within=within)
        if link is not None:
            return link

        field = self.find_field_by_text(text, within=within)
        if field is not None:
            return field

        button = self.find_button_by_label(text, within=within)
        if button is not None:
            return button

    def find_link_by_text(self, text, within=None):
        """Searches for a link with the passed text.
        The comparison is done with normalized whitespace and includes the full
        text within the link, including its subelements' texts.

        :param text: The text to be looked for.
        :type text: string
        :param within: A node object for limiting the scope of the search.
        :type within: :py:class:`ftw.testbrowser.nodes.NodeWrapper`.
        :returns: The link object or `None` if nothing matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.LinkNode`
        """

        text = normalize_spaces(text)
        if within is None:
            within = self

        for link in within.css('a'):
            if normalize_spaces(link.text_content()) == text:
                return link

        return None

    def find_field_by_text(self, text, within=None):
        """Finds a form field which has *text* as label.

        :param text: The text to be looked for.
        :type text: string
        :param within: A node object for limiting the scope of the search.
        :type within: :py:class:`ftw.testbrowser.nodes.NodeWrapper`.
        :returns: A single node object or `None` if nothing matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        if within is None:
            within = self.root

        for form in self.forms.values():
            field = form.find_field(text)
            if field and field.within(within):
                return field

        return None

    def find_button_by_label(self, label, within=None):
        """Finds a form button by its text label.

        :param text: The text to be looked for.
        :type text: string
        :param within: A node object for limiting the scope of the search.
        :type within: :py:class:`ftw.testbrowser.nodes.NodeWrapper`.
        :returns: The button node or `None` if nothing matches.
        :rtype: :py:class:`ftw.testbrowser.form.SubmitButton`
        """

        if within is None:
            within = self.root

        for form in self.forms.values():
            button = form.find_button_by_label(label)
            if button is not None and button.within(within):
                return button

    def find_form_by_field(self, field_label_or_name):
        """Searches for a field and returns the form containing the field.
        The field is searched by label text or field name.
        If no field was found, `None` is returned.

        :param label_or_name: The label or the name of the field.
        :type label_or_name: string
        :returns: The form instance which has the searched fields or `None`
        :rtype: :py:class:`ftw.testbrowser.form.Form`.
        """

        for form in self.forms.values():
            if form.find_field(field_label_or_name):
                return form
        return None

    def find_form_by_fields(self, *labels_or_names):
        """Searches for the form which has fields for the labels passed as
        arguments and returns the form node.

        :returns: The form instance which has the searched fields.
        :rtype: :py:class:`ftw.testbrowser.form.Form`
        :raises: :py:exc:`ftw.testbrowser.exceptions.FormFieldNotFound`
        :raises: :py:exc:`ftw.testbrowser.exceptions.AmbiguousFormFields`
        """

        previous_form = None

        for label_or_name in labels_or_names:
            form = self.find_form_by_field(label_or_name)

            if form is None:
                raise FormFieldNotFound(label_or_name, self.form_field_labels)

            if previous_form is not None and form != previous_form:
                raise AmbiguousFormFields()

            previous_form = form

        return previous_form

    @property
    def form_field_labels(self):
        """A list of label texts and field names of each field in any form on
        the current page.

        The list contains the whitespace normalized label text of the
        each field.
        If there is no label or it has an empty text, the fieldname is
        used instead.

        :returns: A list of label texts (and field names).
        :rtype: list of strings
        """
        return reduce(list.__add__,
                      map(attrgetter('field_labels'),
                          self.forms.values()))

    def click_on(self, text, within=None):
        """Find a link by its text and click on it.

        :param text: The text to be looked for.
        :type text: string
        :param within: A node object for limiting the scope of the search.
        :type within: :py:class:`ftw.testbrowser.nodes.NodeWrapper`.
        :returns: The browser object.
        :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
        .. seealso:: :py:func:`find`
        """
        node = self.find(text)
        if not node:
            raise NoElementFound(query_info=(self, 'click_on', text))

        node.click()
        return self

    @property
    def context(self):
        """Returns the current context (Plone object) of the currently
        viewed page.

        :returns: The Plone context object
        """

        if self.document is None:
            raise ContextNotFound('Not viewing any page.')

        base_tags = self.css('base')
        if len(base_tags) == 0:
            raise ContextNotFound('No <base> tag found on current page.')
        elif len(base_tags) > 1:
            raise ContextNotFound('Unexpectedly found multiple <base> tags.')
        base, = base_tags

        url = base.attrib['href']
        path = urlparse.urlparse(url).path.rstrip('/')
        portal = getSite()
        portal_path = '/'.join(portal.getPhysicalPath())
        if not path.startswith(portal_path):
            raise ContextNotFound((
                'Expected URL path to start with the Plone site'
                ' path "%s" but it is "%s"') % (portal_path, path))

        relative_path = path[len(portal_path + '/'):]
        obj = portal.restrictedTraverse(relative_path)

        # Make sure it returns the context object not a traversable view.
        return filter(IItem.providedBy, aq_chain(obj))[0]

    def parse_as_html(self, html=None):
        """Parse the response document with the HTML parser.

        .. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse_as_xml`
        .. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse`

        :param html: The HTML to parse (default: current response).
        :type html: string
        """
        return self._load_html(html or self.contents, parse_html)

    def parse_as_xml(self, xml=None):
        """Parse the response document with the XML parser.

        .. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse_as_html`
        .. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse`

        :param xml: The XML to parse (default: current response).
        :type xml: string
        """
        return self._load_html(xml or self.contents, lxml.etree.parse)

    def parse(self, xml_or_html):
        """Parse XML or HTML with the default parser.
        For XML mime types the XML parser is used, otherwise the HTML parser.

        .. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse_as_html`
        .. seealso:: :py:mod:`ftw.testbrowser.core.Browser.parse_as_xml`

        :param xml: The XML or HTML to parse.
        :type xml: string
        """

        if self.mimetype in ('text/xml', 'application/xml'):
            return self._load_html(xml_or_html, lxml.etree.parse)
        else:
            return self._load_html(xml_or_html,
                                   parse_html)

    @contextmanager
    def expect_http_error(self, code=None, reason=None):
        """Context manager for expecting certain HTTP errors.
        The ``code`` and ``reason`` arguments may be provided or omitted.
        The values are only asserted if the arguments are provided.
        An assertion error is raised when the HTTP error is not cathed in the
        code block.
        The code block may make a request or reload the browser.

        :param code: The status code to assert.
        :type code: ``int``
        :param reason: The status reason to assert.
        :type reason: ``string``
        :raises: :py:exc:`AssertionError`
        """

        try:
            self._log_exceptions = False
            yield
        except HTTPError, exc:
            if code is not None and code != exc.status_code:
                raise AssertionError(
                    'Expected HTTP error with status code {}, got {}.'.format(
                        code, exc.status_code))
            if reason is not None and reason != exc.status_reason:
                raise AssertionError(
                    'Expected HTTP error with status {!r}, got {!r}.'.format(
                        reason, exc.status_reason))
        else:
            raise AssertionError('Expected a HTTP error but it didn\'t occur.')
        finally:
            self._log_exceptions = True

    @contextmanager
    def expect_unauthorized(self):
        """Context manager for expecting that next request, issued in the
        context manager block, will be unauthorized.
        Plone will redirect to the login form when the user is not authorized.
        In order to detect unauthorized responses, the URL is tested for the
        login view.
        """
        if self.exception_bubbling:
            raise ValueError(
                'The expect_unauthorized context mangaer does not work when'
                ' the exception_bubbling option is enabled.'
                ' Use self.assertRaises(Unauthorized) instead.')

        try:
            yield
        except HTTPError, exc:
            if exc.status_code == 401:
                # Response is "401 Unauthorized", thus user is probably
                # logged in but unauthorized anyway;
                # that's what we expect.
                return
            else:
                raise

        else:
            view_name = urlparse.urlparse(self.url).path.split('/')[-1]
            if view_name == 'require_login':
                # We were redirected to the login form, indicating that the
                # user is not logged in and not authorized;
                # that's what we expected.
                return

        raise AssertionError(
            'Expected request to be unauthorized, but got: {} {} at {}'.format(
                self.status_code, self.status_reason, self.url))

    def clone(self):
        """Creates a new browser instance with a cloned state of the
        current browser. Headers and cookies are copied but not shared.
        The new browser needs to be used as a context manager, eg.:

        with browser.clone() as sub_browser:
            sub_browser.open()


        :returns: A new browser instance.
        :rtype: :py:class:`ftw.testbrowser.core.Browser`
        """
        subbrowser = Browser()(self.app)
        subbrowser.request_library = self.request_library
        subbrowser.session_headers = deepcopy(self.session_headers)
        subbrowser.app = self.app
        self.get_driver().cloned(subbrowser)
        return subbrowser

    def debug(self):
        """Open the current page in your real browser by writing the contents
        into a temporary file and opening it with os.system ``open [FILE]``.

        This is meant to be used in pdb, not in actual code.
        """
        _, path = tempfile.mkstemp(suffix='.html',
                                   prefix='ftw.testbrowser-')
        with open(path, 'w+') as file_:
            source = self.contents
            if isinstance(source, unicode):
                source = source.encode('utf-8')

            file_.write(source)
            cmd = 'open {0}'.format(path)
            print '> {0}'.format(cmd)
            os.system(cmd)

    def _verify_setup(self):
        if self.request_library is None:
            raise BrowserNotSetUpException()
        return True

    def _normalize_url(self, url_or_object, view=None):
        if url_or_object is None:
            url_or_object = getSite().absolute_url()

        if hasattr(url_or_object, 'absolute_url'):
            url = url_or_object.absolute_url()
        else:
            url = url_or_object

        if view is not None:
            parts = list(urlparse.urlparse(url))
            parts[2] = '/'.join((parts[2].rstrip('/'), view))
            url = urlparse.urlunparse(parts)

        if self.url:
            url = urlparse.urljoin(self.url, url)

        return url

    def _load_html(self, html, parser=parse_html):
        self.form_files = {}

        if hasattr(html, 'seek'):
            html.seek(0)

        if isinstance(html, (unicode, str)):
            html = StringIO(html)

        if len(html.read()) == 0:
            self.document = None
            return None
        else:
            html.seek(0)
            self.document = parser(html)

            return html
