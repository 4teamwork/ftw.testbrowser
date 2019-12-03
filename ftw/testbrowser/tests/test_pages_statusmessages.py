from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import nondefault_browsing


@all_drivers
class TestStatusmessages(BrowserTestCase):

    @nondefault_browsing
    def test_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEqual(
            {'info': ['An info message.'],
             'warning': ['A warning message.'],
             'error': ['An error message.']},
            statusmessages.messages(browser=browser))

    @nondefault_browsing
    def test_info_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEqual(['An info message.'],
                         statusmessages.info_messages(browser=browser))

    @nondefault_browsing
    def test_warning_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEqual(['A warning message.'],
                         statusmessages.warning_messages(browser=browser))

    @nondefault_browsing
    def test_error_messages(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEqual(['An error message.'],
                         statusmessages.error_messages(browser=browser))

    @nondefault_browsing
    def test_as_string(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEqual(
            '"[ERROR] An error message.", '
            '"[INFO] An info message.", '
            '"[WARNING] A warning message."',
            statusmessages.as_string(browser=browser))

    @nondefault_browsing
    def test_as_string_with_filtering(self, browser):
        browser.open(view='test-statusmessages')
        self.assertEqual(
            '"[WARNING] A warning message."',
            statusmessages.as_string('warning', browser=browser))

    @nondefault_browsing
    def test_assert_message(self, browser):
        browser.open(view='test-statusmessages')
        self.assertTrue(statusmessages.assert_message('A warning message.',
                                                      browser=browser))

    @nondefault_browsing
    def test_assert_message_failure(self, browser):
        browser.open(view='test-statusmessages?type=info')
        with self.assertRaises(AssertionError) as cm:
            statusmessages.assert_message('a message', browser=browser)

        self.assertEqual('No status message "a message". Current messages:'
                         ' "[INFO] An info message."',
                         str(cm.exception))

    @nondefault_browsing
    def test_assert_no_messages(self, browser):
        browser.open()
        self.assertTrue(statusmessages.assert_no_messages(browser=browser))

    @nondefault_browsing
    def test_assert_no_messages_failure(self, browser):
        browser.open(view='test-statusmessages?type=warning')
        with self.assertRaises(AssertionError) as cm:
            statusmessages.assert_no_messages(browser=browser)

        self.assertEqual('Unexpected status messages:'
                         ' "[WARNING] A warning message."',
                         str(cm.exception))

    @nondefault_browsing
    def test_assert_no_error_messages(self, browser):
        browser.open(view='test-statusmessages?type=warning')
        self.assertEqual(
            {'info': [],
             'warning': ['A warning message.'],
             'error': []},
            statusmessages.messages(browser=browser))

        self.assertTrue(statusmessages.assert_no_error_messages(browser=browser))

    @nondefault_browsing
    def test_assert_no_error_messages_failure(self, browser):
        browser.open(view='test-statusmessages')

        with self.assertRaises(AssertionError) as cm:
            statusmessages.assert_no_error_messages(browser=browser)

        self.assertEqual('Unexpected "error" status messages:'
                         ' "[ERROR] An error message."',
                         str(cm.exception))
