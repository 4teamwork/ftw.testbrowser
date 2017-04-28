from ftw.testbrowser.core import Browser
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.drivers.layers import DefaultDriverFixture
from ftw.testbrowser.exceptions import HTTPClientError
from ftw.testbrowser.exceptions import HTTPServerError


HTTPClientError, HTTPServerError  # noqa


#: The singleton browser instance acting as default browser.
browser = Browser()


def browsing(func):
    """The ``browsing`` decorator is used in tests for automatically setting up
    the browser and passing it into the test function as additional argument:

    .. code:: py

        from ftw.testbrowser import browsing
        from plone.app.testing import PLONE_FUNCTIONAL_TESTING
        from unittest2 import TestCase

        class TestSomething(TestCase):
            layer = PLONE_FUNCTIONAL_TESTING

            @browsing
            def test_login_form(self, browser):
                browser.open(view='login_form')
                self.assertEquals('http://nohost/plone/login_form',
                                  browser.url)
    """

    def test_function(self, *args, **kwargs):
        app = getattr(self, 'layer', {}).get('app', False)
        with browser(app):
            args = list(args) + [browser]
            return func(self, *args, **kwargs)
    test_function.__name__ = func.__name__
    return test_function


#: A plone.testing layer which sets the default driver to Mechanize.
MECHANIZE_BROWSER_FIXTURE = DefaultDriverFixture(LIB_MECHANIZE)

#: A plone.testing layer which sets the default driver to Requests.
REQUESTS_BROWSER_FIXTURE = DefaultDriverFixture(LIB_REQUESTS)
