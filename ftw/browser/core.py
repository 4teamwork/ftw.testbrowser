from ftw.browser.exceptions import BrowserNotSetUpException
from ftw.browser.form import Form
from ftw.browser.interfaces import IBrowser
from lxml.cssselect import CSSSelector
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.testing._z2_testbrowser import Zope2MechanizeBrowser
from zope.component.hooks import getSite
from zope.interface import implements
import lxml
import tempfile
import urllib
import urlparse


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

    @property
    def url(self):
        return self.get_mechbrowser().geturl()

    def login(self, username=TEST_USER_NAME, password=TEST_USER_PASSWORD):
        self.get_mechbrowser().addheaders.append(
            ('Authorization', 'Basic %s:%s' % (username, password)))
        return self

    def css(self, css_selector):
        return self.xpath(CSSSelector(css_selector).path)

    def xpath(self, xpath_selector):
        return self.document.xpath(xpath_selector)

    @property
    def root(self):
        return self.document.getroot()

    @property
    def forms(self):
        return dict([(form.attrib['id'], Form(form)) for form in self.root.forms
                     if form.attrib.get('id', None)])

    def fill(self, values):
        form = Form.find_form_by_labels_or_names(*values.keys())
        return form.fill(values)

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
