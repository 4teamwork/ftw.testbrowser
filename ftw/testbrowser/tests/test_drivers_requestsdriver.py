from ftw.testbrowser import browsing
from ftw.testbrowser.drivers.requestsdriver import RequestsDriver
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.testing import REQUESTS_TESTING
from ftw.testbrowser.tests import FunctionalTestCase
from zope.interface.verify import verifyClass


class TestRequestsDriverImplementation(FunctionalTestCase):
    layer = REQUESTS_TESTING

    def test_implements_interface(self):
        verifyClass(IDriver, RequestsDriver)

    @browsing
    def test_does_not_support_duplicate_request_headers(self, browser):
        browser.get_driver()
        browser.append_request_header('Authorization', 'Basic foo:foo')

        with self.assertRaises(NameError) as cm:
            browser.append_request_header('Authorization', 'Basic foo:bar')

        self.assertEquals(
            'There is already a header "Authorization" and the requests driver'
            ' does not support using the same header multiple times.',
            str(cm.exception))
