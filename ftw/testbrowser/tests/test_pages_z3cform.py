from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import z3cform
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import nondefault_browsing


@all_drivers
class TestZ3cformPageObject(BrowserTestCase):

    @nondefault_browsing
    def test_erroneous_fields(self, browser):
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Folder', browser=browser)
        browser.find('Save').click()

        self.assertEquals(browser.previous_url, browser.url)

        form = browser.css('form#form').first
        self.assertEquals({u'Title': ['Required input is missing.']},
                          z3cform.erroneous_fields(form, browser=browser))
