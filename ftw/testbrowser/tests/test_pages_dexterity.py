from ftw.testbrowser import browsing
from ftw.testbrowser.pages import dexterity
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.tests import FunctionalTestCase


class TestDexterityPageObject(FunctionalTestCase):

    @browsing
    def test_erroneous_fields(self, browser):
        self.grant('Manager')

        browser.login().open()
        factoriesmenu.add('Folder')
        browser.find('Save').click()

        self.assertEquals(browser.previous_url, browser.url)
        self.assertEquals({u'Title': ['Required input is missing.']},
                          dexterity.erroneous_fields())
