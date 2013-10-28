from ftw.testbrowser.core import Browser


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
        with browser(self.layer['app']):
            args = list(args) + [browser]
            return func(self, *args, **kwargs)
    test_function.__name__ = func.__name__
    return test_function
