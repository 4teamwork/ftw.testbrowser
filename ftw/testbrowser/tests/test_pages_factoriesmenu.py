from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase


class TestFactoriesMenu(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    def setUp(self):
        setRoles(self.layer['portal'], TEST_USER_ID, ['Manager'])
        login(self.layer['portal'], TEST_USER_NAME)

    @browsing
    def test_factoriesmenu_visible(self, browser):
        browser.open()
        self.assertFalse(factoriesmenu.visible())
        browser.login(SITE_OWNER_NAME).open()
        self.assertTrue(factoriesmenu.visible())

    @browsing
    def test_addable_types(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        self.assertIn('Folder', factoriesmenu.addable_types())

    @browsing
    def test_addable_types_raises_when_menu_not_visible(self, browser):
        browser.open()
        with self.assertRaises(ValueError) as cm:
            factoriesmenu.addable_types()

        self.assertEquals('Factories menu is not visible.', str(cm.exception))

    @browsing
    def test_adding_content(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Folder')
        self.assertEquals('atct_edit', plone.view())

    @browsing
    def test_adding_unallowed_or_missing_type(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        with self.assertRaises(ValueError) as cm:
            factoriesmenu.add('Unkown Type')

        self.assertTrue(
            str(cm.exception).startswith(
                'The type "Unkown Type" is not addable. Addable types: '),
            str(cm.exception))

    @browsing
    def test_adding_fails_when_no_factoriesmenu_visible(self, browser):
        browser.open()
        with self.assertRaises(ValueError) as cm:
            factoriesmenu.add('Folder')

        self.assertEquals('Cannot add "Folder": no factories menu visible.',
                          str(cm.exception))

    @browsing
    def test_addable_types_works_with_restrictions_entry(self, browser):
        # Regression:
        # The "Restrictions..." entry in the factories menu, as it exists
        # on folders, contains unicode characters and did break everything.
        # This test verifies that this still works.
        folder = create(Builder('folder'))
        browser.login(SITE_OWNER_NAME).visit(folder)
        self.assertIn(u'Restrictions\u2026', factoriesmenu.addable_types())
