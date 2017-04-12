from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import z3cform
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers


@all_drivers
class TestZ3cformPageObject(FunctionalTestCase):

    @browsing
    def test_erroneous_fields(self, browser):
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Folder')
        browser.find('Save').click()

        self.assertEquals(browser.previous_url, browser.url)

        form = browser.css('form#form').first
        self.assertEquals({u'Title': ['Required input is missing.']},
                          z3cform.erroneous_fields(form))
