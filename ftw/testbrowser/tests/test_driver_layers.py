from ftw.testbrowser import browsing
from ftw.testbrowser import MECHANIZE_BROWSER_FIXTURE
from ftw.testbrowser import REQUESTS_BROWSER_FIXTURE
from ftw.testbrowser import TRAVERSAL_BROWSER_FIXTURE
from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.core import LIB_TRAVERSAL
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from unittest2 import TestCase


class TestMechanizeFixture(TestCase):

    layer = FunctionalTesting(
        bases=(PLONE_FIXTURE,
               MECHANIZE_BROWSER_FIXTURE),
        name='functional:mechanize')

    @browsing
    def test(self, browser):
        self.assertEquals(LIB_MECHANIZE, browser.get_driver().LIBRARY_NAME)


class TestRequestsFixture(TestCase):

    layer = FunctionalTesting(
        bases=(PLONE_FIXTURE,
               REQUESTS_BROWSER_FIXTURE),
        name='functional:requests')

    @browsing
    def test(self, browser):
        self.assertEquals(LIB_REQUESTS, browser.get_driver().LIBRARY_NAME)


class TestTraversalFixture(TestCase):

    layer = FunctionalTesting(
        bases=(PLONE_FIXTURE,
               TRAVERSAL_BROWSER_FIXTURE),
        name='functional:traversal')

    @browsing
    def test(self, browser):
        self.assertEquals(LIB_TRAVERSAL, browser.get_driver().LIBRARY_NAME)
