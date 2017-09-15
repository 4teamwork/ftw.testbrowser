from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import nondefault_browsing


@all_drivers
class TestFactoriesMenu(BrowserTestCase):

    @nondefault_browsing
    def test_factoriesmenu_visible(self, browser):
        self.grant('Manager')
        browser.open()
        self.assertFalse(factoriesmenu.visible(browser=browser))
        browser.login().open()
        self.assertTrue(factoriesmenu.visible(browser=browser))

    @nondefault_browsing
    def test_addable_types(self, browser):
        self.grant('Manager')
        browser.login().open()
        self.assertIn('Folder', factoriesmenu.addable_types(browser=browser))

    @nondefault_browsing
    def test_addable_types_raises_when_menu_not_visible(self, browser):
        browser.open()
        with self.assertRaises(ValueError) as cm:
            factoriesmenu.addable_types(browser=browser)

        self.assertEquals('Factories menu is not visible.', str(cm.exception))

    @nondefault_browsing
    def test_adding_content(self, browser):
        self.grant('Manager')
        browser.login().open()
        factoriesmenu.add('Folder', browser=browser)
        self.assertEquals(self.portal.portal_url() + '/++add++Folder', browser.url)

    @nondefault_browsing
    def test_adding_unallowed_or_missing_type(self, browser):
        self.grant('Manager')
        browser.login().open()
        with self.assertRaises(ValueError) as cm:
            factoriesmenu.add('Unkown Type', browser=browser)

        self.assertTrue(
            str(cm.exception).startswith(
                'The type "Unkown Type" is not addable. Addable types: '),
            str(cm.exception))

    @nondefault_browsing
    def test_adding_fails_when_no_factoriesmenu_visible(self, browser):
        browser.open()
        with self.assertRaises(ValueError) as cm:
            factoriesmenu.add('Folder', browser=browser)

        self.assertEquals('Cannot add "Folder": no factories menu visible.',
                          str(cm.exception))

    @nondefault_browsing
    def test_addable_types_works_with_restrictions_entry(self, browser):
        self.grant('Manager')
        # Regression:
        # The "Restrictions..." entry in the factories menu, as it exists
        # on folders, contains unicode characters and did break everything.
        # This test verifies that this still works.
        folder = create(Builder('folder'))
        browser.login().visit(folder)
        self.assertIn(u'Restrictions\u2026',
                      factoriesmenu.addable_types(browser=browser))
