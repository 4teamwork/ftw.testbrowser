from StringIO import StringIO
from ftw.testbrowser.exceptions import AmbiguousFormFields
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.exceptions import FormFieldNotFound
from ftw.testbrowser.form import Form
from ftw.testbrowser.interfaces import IBrowser
from ftw.testbrowser.nodes import wrapped_nodes
from ftw.testbrowser.utils import normalize_spaces
from lxml.cssselect import CSSSelector
from mechanize import BrowserStateError
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from zope.component.hooks import getSite
from zope.interface import implements
import json
import lxml
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

    def __enter__(self):
        if self.next_app is None:
            raise BrowserNotSetUpException()

        self.app = self.next_app
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (exc_type or exc_value) and self.response:
            _, path = tempfile.mkstemp(suffix='.html',
                                       prefix='ftw.testbrowser-')
            with open(path, 'w+') as file_:
                self.response.seek(0)
                file_.write(self.response.read())
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
        data = self._prepare_post_data(data)
        self.response = self.get_mechbrowser().open(url, data=data)
        return self.open_html(self.response)

    def open_html(self, html):
        """Opens a HTML page in the browser without doing a request.
        The passed ``html`` may be a string or a file-like stream.

        :param html: The HTML content to load in the browser.
        :type html: string or file-like object
        :returns: The browser object.
        """

        if hasattr(html, 'seek'):
            html.seek(0)

        if isinstance(html, (unicode, str)):
            html = StringIO(html)

        self.document = lxml.html.parse(html)
        return self

    def visit(self, *args, **kwargs):
        """Visit is an alias for :py:func:`open`.

        .. seealso:: :py:func:`open`
        """
        return self.open(*args, **kwargs)

    @property
    def contents(self):
        """The source of the current page (usually HTML).
        """
        self._verify_setup()
        self.response.seek(0)
        return self.response.read()

    @property
    def json(self):
        """If the current page is JSON only, this can be used for getting the
        converted JSON data as python data structure.
        """
        return json.loads(self.contents)

    @property
    def url(self):
        """The URL of the current page.
        """
        return self.get_mechbrowser().geturl()

    def login(self, username=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        """Login a user by setting the ``Authorization`` header.
        Use the :py:func:`reset` method for logging out and clearing
        everything.
        """
        self.get_mechbrowser().addheaders.append(
            ('Authorization', 'Basic %s:%s' % (username, password)))
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
            forms[key] = Form(node)

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
        form = Form.find_form_by_labels_or_names(*values.keys())
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

        try:
            form = Form.find_form_by_labels_or_names(text)
        except (AmbiguousFormFields, FormFieldNotFound):
            return None

        field = form.find_field(text)
        if field is not None and field.within(within):
            return field
        else:
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

    def _prepare_post_data(self, data):
        if not data:
            return None

        if isinstance(data, dict):
            data = data.items()

        return urllib.urlencode(data)
