from ftw.testbrowser import browsing
from ftw.testbrowser.exceptions import HTTPError
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import capture_streams
from ftw.testbrowser.tests.helpers import register_view
from StringIO import StringIO
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
        self.assertEquals(
            '{}/failing-view\n'.format(self.portal.absolute_url()) +
            'Traceback (innermost last):\n'
            '  Module ZPublisher.Publish, line 138, in publish\n'
            '  Module ZPublisher.mapply, line 77, in mapply\n'
            '  Module ZPublisher.Publish, line 48, in call_object\n'
            '  Module ftw.testbrowser.tests.test_log, line 18, in __call__\n'
            'ValueError: The value is wrong.',
            output)

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

        self.assertEquals(
            '', stderr.getvalue(),
            'No errors should be logged when using expect_http_error')
