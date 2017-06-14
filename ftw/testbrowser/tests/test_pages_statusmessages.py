from ftw.testbrowser import browsing
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestStatusmessages(BrowserTestCase):

    @browsing
    def test_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEquals(
            {'info': ['An info message.'],
             'warning': ['A warning message.'],
             'error': ['An error message.']},
            statusmessages.messages())

    @browsing
    def test_info_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEquals(['An info message.'],
                          statusmessages.info_messages())

    @browsing
    def test_warning_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEquals(['A warning message.'],
                          statusmessages.warning_messages())

    @browsing
    def test_error_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEquals(['An error message.'],
                          statusmessages.error_messages())

    @browsing
    def test_as_string(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEquals(
            '"[ERROR] An error message.", '
            '"[INFO] An info message.", '
            '"[WARNING] A warning message."',
            statusmessages.as_string())

    @browsing
    def test_as_string_with_filtering(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEquals(
            '"[WARNING] A warning message."',
            statusmessages.as_string('warning'))

    @browsing
    def test_assert_message(self, browser):
        browser.open(view='test-statusmessages')
        self.assertTrue(statusmessages.assert_message('A warning message.'))

    @browsing
    def test_assert_message_failure(self, browser):
        browser.open(view='test-statusmessages?type=info')
        with self.assertRaises(AssertionError) as cm:
            statusmessages.assert_message('a message')

        self.assertEquals('No status message "a message". Current messages:'
                          ' "[INFO] An info message."',
                          str(cm.exception))

    @browsing
    def test_assert_no_messages(self, browser):
        browser.open()
        self.assertTrue(statusmessages.assert_no_messages())

    @browsing
    def test_assert_no_messages_failure(self, browser):
        browser.open(view='test-statusmessages?type=warning')
        with self.assertRaises(AssertionError) as cm:
            statusmessages.assert_no_messages()

        self.assertEquals('Unexpected status messages:'
                          ' "[WARNING] A warning message."',
                          str(cm.exception))

    @browsing
    def test_assert_no_error_messages(self, browser):
        browser.open(view='test-statusmessages?type=warning')
        self.assertEquals(
            {'info': [],
             'warning': ['A warning message.'],
             'error': []},
            statusmessages.messages())

        self.assertTrue(statusmessages.assert_no_error_messages())

    @browsing
    def test_assert_no_error_messages_failure(self, browser):
        browser.open(view='test-statusmessages')

        with self.assertRaises(AssertionError) as cm:
            statusmessages.assert_no_error_messages()

        self.assertEquals('Unexpected "error" status messages:'
                          ' "[ERROR] An error message."',
                          str(cm.exception))
