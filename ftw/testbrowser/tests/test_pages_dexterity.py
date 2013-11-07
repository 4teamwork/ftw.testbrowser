from ftw.testbrowser import browsing
from ftw.testbrowser.pages import dexterity
from ftw.testbrowser.pages import factoriesmenu
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestDexterityPageObject(TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    @browsing
    def test_erroneous_fields(self, browser):
        browser.login().open()
        factoriesmenu.add('Folder')
        browser.find('Save').click()
        self.assertEquals(browser.previous_url, browser.url)
        self.assertEquals({u'Title': ['Required input is missing.']},
                          dexterity.erroneous_fields())
