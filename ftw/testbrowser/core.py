from StringIO import StringIO
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.exceptions import ContextNotFound
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.exceptions import ZServerRequired
from ftw.testbrowser.interfaces import IBrowser
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.utils import normalize_spaces
from ftw.testbrowser.utils import verbose_logging
from lxml.cssselect import CSSSelector
from mechanize import BrowserStateError
from operator import attrgetter
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from requests.structures import CaseInsensitiveDict
from zope.component.hooks import getSite
from zope.interface import implements
import json
import lxml
import requests
import tempfile
import urllib
import urlparse


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
        self.next_app = None
        self.app = None
        self.mechbrowser = None
        self.response = None
        self.document = None
        self.previous_url = None
        self._authentication = None

    def __enter__(self):
        if self.next_app is None:
            raise BrowserNotSetUpException()

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

    def open(self, url_or_object=None, data=None, view=None):
        """Opens a page in the browser.

        :param url_or_object: A full qualified URL or a Plone object (which has
          an ``absolute_url`` method). Defaults to the Plone Site URL.
        :param data: A dict with data which is posted using a `POST` request.
        :type data: dict
        :param view: The name of a view which will be added at the end of the
          current URL.
        :type view: string

        .. seealso:: :py:func:`visit`
        """
        self._verify_setup()
        try:
            self.previous_url = self.url
        except BrowserStateError:
            pass
        url = self._normalize_url(url_or_object, view=view)
        self._open_with_mechanize(url, data=data)
        return self

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
        try:
            self.previous_url = self.url
        except BrowserStateError:
            pass

        url = self._normalize_url(url_or_object, view=view)
        self._open_with_requests(url, data=data, method=method, headers=headers)
        return self

    def _open_with_mechanize(self, url, data=None):
        """Opens an internal request with the mechanize library.
        Since the request is internally dispatched, no open server port is required.

        :param url: A full qualified URL.
        :type url: string
        :param data: A dict with data which is posted using a `POST` request.
        :type data: dict
        """

        data = self._prepare_post_data(data)
        self.response = self.get_mechbrowser().open(url, data=data)
        self._load_html(self.response)

    def _open_with_requests(self, url, data=None, method='GET', headers=None):
        """Opens a request with the requests library.
        Since this request is actually executed over TCP/IP, an open server port
        is required.

        :param url: A full qualified URL.
        :type url: string
        :param data: A dict with data which is posted using a `POST` request or
          a string with data.
        :type data: dict or string
        :param method: The request method, defaults to 'GET'.
        :type method: string
        :param headers: A dict with custom headers for this request.
        :type headers: dict
        """

        if urlparse.urlparse(url).hostname == 'nohost':
            raise ZServerRequired()

        with verbose_logging():
            self.response = requests.request(method, url, data=data,
                                             auth=self._authentication,
                                             headers=headers)

        self._load_html(self.response)

    @property
    def contents(self):
        """The source of the current page (usually HTML).
        """
        self._verify_setup()

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
        else:
            return CaseInsensitiveDict(self.response.info().items())

    def append_request_header(self, name, value):
        """Add a new permanent request header which is sent with every request
        until it is cleared.

        HTTP allows multiple request headers with the same name.
        Therefore this method does not replace existing names.
        Use `replace_request_header` for replacing headers.

        :param name: Name of the request header
        :type name: string
        :param value: Value of the request header
        :type value: string

        .. seealso:: :py:func:`replace_request_header`
        .. seealso:: :py:func:`clear_request_header`
        """
        self.get_mechbrowser().addheaders.append((name, value))

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
        addheaders = self.get_mechbrowser().addheaders

        for header_name, value in addheaders[:]:
            if header_name == name:
                addheaders.remove((header_name, value))

    @property
    def cookies(self):
        """A read-only dict of current cookies.
        """
        mechbrowser = self.get_mechbrowser()
        cookiejar = mechbrowser._ua_handlers["_cookies"].cookiejar
        cookies = {}
        for cookie in cookiejar:
            cookies[cookie.name] = vars(cookie)
        return cookies

    @property
    def url(self):
        """The URL of the current page.
        """
        return self.get_mechbrowser().geturl()

    def login(self, username=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        """Login a user by setting the ``Authorization`` header.
        """

        if hasattr(username, 'getUserName'):
            username = username.getUserName()

        self.replace_request_header('Authorization',
                                    'Basic {0}:{1}'.format(username, password))
        self._authentication = (username, password)
        return self

    def logout(self):
        """Logout the current user by removing the ``Authorization`` header.
        """
        self._authentication = None
        self.clear_request_header('Authorization')
        return self

    def css(self, css_selector):
        """Select one or more HTML nodes by using a *CSS* selector.

        :param css_selector: The CSS selector.
        :type css_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.xpath(CSSSelector(css_selector).path)

    @wrapped_nodes
    def xpath(self, xpath_selector):
        """Select one or more HTML nodes by using an *xpath* selector.

        :param xpath_selector: The xpath selector.
        :type xpath_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.document.xpath(xpath_selector)

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
        if self.mechbrowser is None:
            self.mechbrowser = Zope2MechanizeBrowser(self.app)
            self.get_mechbrowser().addheaders.append((
                    'X-zope-handle-errors', 'False'))
        return self.mechbrowser

    def _verify_setup(self):
        if self.app is None:
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

        to_utf8 = (lambda val: isinstance(val, unicode)
                   and val.encode('utf-8') or val)
        data = dict(map(lambda item: map(to_utf8, item), data))

        return urllib.urlencode(data)
