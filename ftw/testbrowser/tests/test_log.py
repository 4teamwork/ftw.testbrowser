from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPError
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import capture_streams
from ftw.testbrowser.tests.helpers import register_view
from six import StringIO
from zope.publisher.browser import BrowserView


@all_drivers
class TestExceptionLogger(BrowserTestCase):

    @browsing
    def test_exceptions_are_printed_to_stderr(self, browser):
        class FailingView(BrowserView):
            def __call__(self):
                raise ValueError('The value is wrong.')

        with register_view(FailingView, 'failing-view'):
            stderr = StringIO()
            with capture_streams(stderr=stderr):
                with self.assertRaises(HTTPError):
                    browser.open(view='failing-view')

        output = stderr.getvalue().strip()
        # The output starts with a random error_log id => strip it.
        self.assertTrue(output, 'No output in stderr')
        output = output.split(' ', 1)[1]
        expected_start = '{}/failing-view\n'.format(
            self.portal.absolute_url()) + 'Traceback (innermost last):\n'
        expected_end = 'ValueError: The value is wrong.'
        self.assertTrue(output.startswith(expected_start), 'Unexpected traceback')
        self.assertTrue(output.endswith(expected_end), 'Unexpected traceback')

    @browsing
    def test_no_exceptions_logged_when_errors_expected(self, browser):
        class FailingView(BrowserView):
            def __call__(self):
                raise ValueError('The value is wrong.')

        with register_view(FailingView, 'failing-view'):
            stderr = StringIO()
            with capture_streams(stderr=stderr):
                with browser.expect_http_error():
                    browser.open(view='failing-view')

        self.assertEqual(
            '', stderr.getvalue(),
            'No errors should be logged when using expect_http_error')
