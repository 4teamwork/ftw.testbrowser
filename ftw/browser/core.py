from ftw.browser.exceptions import AmbiguousFormFields
from ftw.browser.exceptions import BrowserNotSetUpException
from ftw.browser.exceptions import FormFieldNotFound
from ftw.browser.form import Form
from ftw.browser.interfaces import IBrowser
from ftw.browser.nodes import wrapped_nodes
from lxml.cssselect import CSSSelector
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from zope.component.hooks import getSite
from zope.interface import implements
import lxml
import re
import tempfile
import urllib
import urlparse


def normalize_spaces(text):
    return re.sub(r'\s{1,}', ' ', text)


class Browser(object):
    implements(IBrowser)

    def __init__(self):
        self.reset()

    def __call__(self, app):
        self.next_app = app
        return self

    def reset(self):
        self.next_app = None
        self.app = None
        self.mechbrowser = None
        self.response = None
        self.document = None

    def __enter__(self):
        if self.next_app is None:
            raise BrowserNotSetUpException()

        self.app = self.next_app
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if (exc_type or exc_value) and self.response:
            _, path = tempfile.mkstemp(suffix='.html', prefix='ftw.browser-')
            with open(path, 'w+') as file_:
                self.response.seek(0)
                file_.write(self.response.read())
            print '\nftw.browser dump:', path,

        self.reset()

    def open(self, url_or_object=None, data=None, view=None):
        self._verify_setup()
        url = self._normalize_url(url_or_object, view=view)
        data = self._prepare_post_data(data)
        self.response = self.get_mechbrowser().open(url, data=data)
        self.document = lxml.html.parse(self.response)
        return self

    def visit(self, *args, **kwargs):
        return self.open(*args, **kwargs)

    @property
    def url(self):
        return self.get_mechbrowser().geturl()

    def login(self, username=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        self.get_mechbrowser().addheaders.append(
            ('Authorization', 'Basic %s:%s' % (username, password)))
        return self

    def css(self, css_selector):
        return self.xpath(CSSSelector(css_selector).path)

    @wrapped_nodes
    def xpath(self, xpath_selector):
        return self.document.xpath(xpath_selector)

    @property
    def root(self):
        return self.document.getroot()

    @property
    def forms(self):
        forms = {}

        for index, node in enumerate(self.css('form')):
            key = node.attrib.get('id', node.attrib.get('name', 'form-%s' % index))
            forms[key] = Form(node)

        return forms

    def fill(self, values):
        form = Form.find_form_by_labels_or_names(*values.keys())
        return form.fill(values)

    def find(self, text):
        """Find an element by text.
        """
        link = self.find_link_by_text(text)
        if link is not None:
            return link

        field = self.find_field_by_text(text)
        if field is not None:
            return field

        button = self.find_button_by_label(text)
        if button is not None:
            return button

    def find_link_by_text(self, text):
        """Find a link by text.
        """
        text = normalize_spaces(text)

        for link in self.css('a'):
            if normalize_spaces(link.text_content()) == text:
                return link

        return None

    def find_field_by_text(self, text):
        """Finds a form field by text.
        """
        try:
            form = Form.find_form_by_labels_or_names(text)
        except (AmbiguousFormFields, FormFieldNotFound):
            return None

        return form.find_field(text)

    def find_button_by_label(self, label):
        """Finds a form button by its text label.
        """
        for form in self.forms.values():
            button = form.find_button_by_label(label)
            if button is not None:
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
