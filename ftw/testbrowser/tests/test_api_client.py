from ftw.testbrowser import api_client
from ftw.testbrowser import restapi
from ftw.testbrowser.core import APIClient
from ftw.testbrowser.exceptions import BlankPage
from ftw.testbrowser.exceptions import BrowserNotSetUpException
from ftw.testbrowser.exceptions import HTTPClientError
from ftw.testbrowser.exceptions import HTTPServerError
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import capture_streams
from ftw.testbrowser.tests.helpers import register_view
from plone.restapi.services import Service
from StringIO import StringIO
from zExceptions import BadRequest
from zope.globalrequest import getRequest


@all_drivers
class TestAPIClientCore(BrowserTestCase):

    @restapi
    def test_contents(self, api_client):
        api_client.login().open()
        expected_contents = {
            u'parent': {},
            u'title': u'Plone site',
            u'is_folderish': True,
            u'@components': {
                u'breadcrumbs': {u'@id': u'http://nohost/plone/@breadcrumbs'},
                u'navigation': {u'@id': u'http://nohost/plone/@navigation'},
                u'actions': {u'@id': u'http://nohost/plone/@actions'},
            },
            u'@type': u'Plone Site',
            u'items_total': 0,
            u'items': [],
            u'@id': u'http://nohost/plone',
            u'id': u'plone',
        }
        self.assertItemsEqual(expected_contents, api_client.contents)

    def test_contents_verifies_setup(self):
        with self.assertRaises(BrowserNotSetUpException):
            APIClient().contents

    @restapi
    def test_contents_raises_when_on_blank_page(self, api_client):
        with self.assertRaises(BlankPage) as cm:
            api_client.contents
        self.assertEquals('The browser is on a blank page.', str(cm.exception))

    @restapi
    def test_url(self, api_client):
        api_client.login().open()
        self.assertEquals(self.layer['portal'].absolute_url(), api_client.url)

    @restapi
    def test_status_is_exposed(self, api_client):
        api_client.login().open()
        self.assertEquals(200, api_client.status_code)
        self.assertEquals('OK', api_client.status_reason.upper())

    @restapi
    def test_raises_404_as_client_error(self, api_client):
        with self.assertRaises(HTTPClientError) as cm:
            api_client.login().open(endpoint='missing')

        self.assertEquals(404, cm.exception.status_code)
        self.assertEquals('Not Found', cm.exception.status_reason)
        self.assertEquals('404 Not Found', str(cm.exception))

        with self.assertRaises(HTTPClientError):
            api_client.reload()

        api_client.raise_http_errors = False
        api_client.reload()

    @restapi
    def test_raises_500_as_server_error(self, api_client):
        class ViewWithError(Service):
            def __call__(self):
                raise ValueError('The value is wrong.')

        with register_view(ViewWithError, 'endpoint-with-error'):
            with capture_streams(stderr=StringIO()):
                with self.assertRaises(HTTPServerError) as cm:
                    api_client.open(endpoint='endpoint-with-error')

            self.assertEquals(500, cm.exception.status_code)
            self.assertEquals('Internal Server Error', cm.exception.status_reason)

            with capture_streams(stderr=StringIO()):
                with self.assertRaises(HTTPServerError):
                    api_client.reload()

            api_client.raise_http_errors = False
            with capture_streams(stderr=StringIO()):
                api_client.reload()

    @restapi
    def test_expect_http_error(self, api_client):
        class GetRecordById(Service):
            def __call__(self):
                raise BadRequest('Missing "id" parameter.')

        with register_view(GetRecordById, 'get-record-by-id'):
            with api_client.expect_http_error():
                api_client.open(endpoint='get-record-by-id')

    @restapi
    def test_expect_http_error_raises_when_no_error_happens(self, api_client):
        with self.assertRaises(AssertionError) as cm:
            with api_client.expect_http_error():
                api_client.login().open()
        self.assertEquals('Expected a HTTP error but it didn\'t occur.', str(cm.exception))

    @restapi
    def test_expect_http_error_and_assert_correct_status_code(self, api_client):
        with api_client.expect_http_error(code=404):
            api_client.open(endpoint='no-such-endpoint')

    @restapi
    def test_expect_http_error_and_assert_incorrect_status_code(self, api_client):
        with self.assertRaises(AssertionError) as cm:
            with api_client.expect_http_error(code=400):
                api_client.login().open(endpoint='no-such-endpoint')
        self.assertEquals('Expected HTTP error with status code 400, got 404.', str(cm.exception))

    @restapi
    def test_expect_http_error_and_assert_correct_status_reason(self, api_client):
        with api_client.expect_http_error(reason='Not Found'):
            api_client.login().open(endpoint='no-such-endpoint')

    @restapi
    def test_expect_http_error_and_assert_incorrect_status_reason(self, api_client):
        with self.assertRaises(AssertionError) as cm:
            with api_client.expect_http_error(reason='Bad Request'):
                api_client.login().open(endpoint='no-such-endpoint')
        self.assertEquals('Expected HTTP error with status \'Bad Request\', got \'Not Found\'.', str(cm.exception))

    @restapi
    def test_expect_unauthorized_successful(self, api_client):
        with api_client.expect_unauthorized():
            api_client.open(endpoint='@navigation')

    @restapi
    def test_expect_unauthorized_failing(self, api_client):
        with self.assertRaises(AssertionError) as cm:
            with api_client.expect_unauthorized():
                api_client.login().open()
        # We uppercase these to get around variance between some of the drivers
        expected_message = 'Expected request to be unauthorized, but got: 200 OK at {}'.format(
            self.portal.absolute_url()).upper()
        message = str(cm.exception).upper()
        self.assertEqual(expected_message, message)

    @restapi
    def test_opening_preserves_global_request(self, api_client):
        api_client.login().open()
        self.assertIsNotNone(getRequest())

    def test_reset_does_not_break_context_manager(self):
        with api_client(self.layer['app']):
            api_client.login().open()
            api_client.reset()
            api_client.login().open()

    def test_nesting_context_manager_not_allowed(self):
        with api_client:
            with self.assertRaises(ValueError) as cm:
                with api_client:
                    pass
            self.assertEquals('Nesting api client context manager is not allowed.', str(cm.exception))
