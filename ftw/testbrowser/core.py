from StringIO import StringIO
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.exceptions import ContextNotFound
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.exceptions import ZServerRequired
from ftw.testbrowser.interfaces import IBrowser
from ftw.testbrowser.nodes import wrap_nodes
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.utils import normalize_spaces
from ftw.testbrowser.utils import verbose_logging
from lxml.cssselect import CSSSelector
from operator import attrgetter
from requests.structures import CaseInsensitiveDict
from zope.component.hooks import getSite
from zope.interface import implements
import json
import lxml
import lxml.html
import os
import pkg_resources
import requests
import tempfile
import urllib
import urlparse


try:
    pkg_resources.get_distribution('plone.app.testing')
except pkg_resources.DistributionNotFound:
    TEST_USER_NAME = 'test-user'
    TEST_USER_PASSWORD = 'secret'
else:
    from plone.app.testing import TEST_USER_NAME
    from plone.app.testing import TEST_USER_PASSWORD

try:
    pkg_resources.get_distribution('zope.testbrowser')
except pkg_resources.DistributionNotFound:
    HAS_PLONE_EXTRAS = False
else:
    HAS_PLONE_EXTRAS = True
    from plone.testing._z2_testbrowser import Zope2MechanizeBrowser


#: Constant for choosing the mechanize library (interally dispatched requests)
LIB_MECHANIZE = 'mechanize library'

#: Constant for choosing the requests library (actual requests)
LIB_REQUESTS = 'requests library'


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
    """

    implements(IBrowser)

    def __init__(self):
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
        self.previous_request_library = None
        self.next_app = None
        self.app = None
        self.mechbrowser = None
        self.response = None
        self.document = None
        self.previous_url = None
        self.form_files = {}

        self.previous_request = None
        self.requests_session = requests.Session()

    def __enter__(self):
        if self.request_library is None:
            if self.next_app is None:
                self.request_library = LIB_REQUESTS
            else:
                self.request_library = LIB_MECHANIZE

        if self.app is None:
            self.app = self.next_app
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (exc_type or exc_value) and self.response is not None:
            _, path = tempfile.mkstemp(suffix='.html',
                                       prefix='ftw.testbrowser-')
            with open(path, 'w+') as file_:
                source = self.contents
                if isinstance(source, unicode):
                    source = source.encode('utf-8')
                file_.write(source)
            print '\nftw.testbrowser dump:', path,

        self.reset()

    def open(self, url_or_object=None, data=None, view=None, library=None):
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
        :param data: A dict with data which is posted using a `POST` request.
        :type data: dict
        :param view: The name of a view which will be added at the end of the
          current URL.
        :type view: string
        :param library: Lets you explicitly choose the request library to be
          used for this request.
        :type library: ``LIB_MECHANIZE`` or ``LIB_REQUESTS``

        .. seealso:: :py:func:`visit`
        .. seealso:: :py:const:`LIB_MECHANIZE`
        .. seealso:: :py:const:`LIB_REQUESTS`
        """
        self._verify_setup()
        library = library or self.request_library
        url = self._normalize_url(url_or_object, view=view)

        if library == LIB_MECHANIZE:
            self._open_with_mechanize(url, data=data)

        elif library == LIB_REQUESTS:
            self._open_with_requests(url, data=data)

        return self

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
        self.response = self._load_html(html)
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
        self._open_with_requests(url, data=data,
                                 method=method, headers=headers)
        return self

    def _open_with_mechanize(self, url, data=None):
        """Opens an internal request with the mechanize library.
        Since the request is internally dispatched, no open server
        port is required.

        :param url: A full qualified URL.
        :type url: string
        :param data: A dict with data which is posted using a `POST` request.
        :type data: dict
        """
        args = locals().copy()
        del args['self']
        self.previous_request = ('_open_with_mechanize', args)

        self.previous_url = self.url
        data = self._prepare_post_data(data)
        try:
            self.response = self.get_mechbrowser().open(url, data=data)
        except:
            self.response = None
            raise
        self._load_html(self.response)
        self.previous_request_library = LIB_MECHANIZE

    def _open_with_requests(self, url, data=None, method='GET', headers=None):
        """Opens a request with the requests library.
        Since this request is actually executed over TCP/IP,
        an open server port is required.

        :param url: A full qualified URL.
        :type url: string
        :param data: A dict with data which is posted using a `POST` request or
          a string with data.
        :type data: dict or string
        :param method: The request method, defaults to 'GET', unless ``data``
          is provided, then its set to 'POST'.
        :type method: string
        :param headers: A dict with custom headers for this request.
        :type headers: dict
        """
        args = locals().copy()
        del args['self']
        self.previous_request = ('_open_with_requests', args)

        self.previous_url = self.url
        if urlparse.urlparse(url).hostname == 'nohost':
            raise ZServerRequired()

        if data and method == 'GET':
            method = 'POST'

        with verbose_logging():
            try:
                self.response = self.requests_session.request(
                    method, url, data=data, headers=headers)
            except:
                self.response = None

        self._load_html(self.response)
        self.previous_request_library = LIB_REQUESTS

    def reload(self):
        """Reloads the current page by redoing the previous requests with
        the same arguments.
        This applies for GET as well as POST requests.

        :raises: :py:exc:`ftw.testbrowser.exceptions.BlankPage`
        """
        if self.previous_request is None:
            raise BlankPage('Cannot reload.')

        request_opener_name, arguments = self.previous_request
        request_opener = getattr(self, request_opener_name)
        request_opener(**arguments)
        return self

    @property
    def contents(self):
        """The source of the current page (usually HTML).
        """
        self._verify_setup()

        if self.response is None:
            raise BlankPage()

        if isinstance(self.response, requests.Response):
            return self.response.content
        else:
            self.response.seek(0)
            return self.response.read()

    @property
    def json(self):
        """If the current page is JSON only, this can be used for getting the
        converted JSON data as python data structure.
        """
        return json.loads(self.contents)

    @property
    def headers(self):
        """A dict of response headers.
        """
        if isinstance(self.response, requests.Response):
            return self.response.headers
        elif getattr(self.response, 'info', None) is not None:
            return CaseInsensitiveDict(self.response.info().items())
        else:
            # Page was opened with open_html - we have no response headers.
            return {}

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

        self.requests_session.headers.update({name: value})

        try:
            self.get_mechbrowser().addheaders.append((name, value))
        except BrowserNotSetUpException:
            pass

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

        if name in self.requests_session.headers:
            del self.requests_session.headers[name]

        try:
            addheaders = self.get_mechbrowser().addheaders
        except BrowserNotSetUpException:
            pass
        else:
            for header_name, value in addheaders[:]:
                if header_name == name:
                    addheaders.remove((header_name, value))

    @property
    def cookies(self):
        """A read-only dict of current cookies.
        """
        cookies = {}

        if self.previous_request_library is LIB_MECHANIZE:
            mechbrowser = self.get_mechbrowser()
            cookiejar = mechbrowser._ua_handlers["_cookies"].cookiejar
            for cookie in cookiejar:
                cookies[cookie.name] = vars(cookie)

        elif self.previous_request_library is LIB_REQUESTS:
            cookiejar = self.requests_session.cookies
            for domain_cookies in cookiejar._cookies.values():
                for path_cookies in domain_cookies.values():
                    for cookie_name, cookie in path_cookies.items():
                        cookies[cookie_name] = vars(cookie)

        return cookies

    @property
    def url(self):
        """The URL of the current page.
        """
        if not self.response:
            return None

        if self.previous_request_library is LIB_MECHANIZE:
            return self.get_mechbrowser().geturl()
        elif self.previous_request_library is LIB_REQUESTS:
            return self.response.url

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
        return wrap_nodes(self.document.xpath(xpath_selector),
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
        return portal.restrictedTraverse(relative_path)

    def get_mechbrowser(self):
        self._verify_setup()

        if not HAS_PLONE_EXTRAS:
            raise ImportError(
                'Could not import zope.testbrowser.'
                ' Please install ftw.testbrowser[plone] extras.')

        if self.app is None:
            raise BrowserNotSetUpException()

        if self.mechbrowser is None:
            self.mechbrowser = Zope2MechanizeBrowser(self.app)
            self.get_mechbrowser().addheaders.append((
                    'X-zope-handle-errors', 'False'))
        return self.mechbrowser

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

        if self.mechbrowser:
            subbrowser.mechbrowser = Zope2MechanizeBrowser(self.app)
            mech_parent = self.mechbrowser
            mech_child = subbrowser.mechbrowser
            cookiejar = mech_parent._ua_handlers['_cookies'].cookiejar
            mech_child.set_cookiejar(cookiejar)
            mech_child.addheaders = mech_parent.addheaders[:]

        req_parent = self.requests_session
        req_child = subbrowser.requests_session
        req_child.headers = req_parent.headers.copy()
        req_child.cookies = requests.cookies.merge_cookies(
            req_parent.cookies, {})

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

        return url

    def _load_html(self, html):
        self.form_files = {}

        if hasattr(html, 'seek'):
            html.seek(0)

        if isinstance(html, (unicode, str)):
            html = StringIO(html)

        if isinstance(html, requests.Response):
            html = StringIO(html.content)

        if len(html.read()) == 0:
            self.document = None
            return None
        else:
            html.seek(0)
            self.document = lxml.html.parse(html)
            return html

    def _prepare_post_data(self, data):
        if not data:
            return None

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
