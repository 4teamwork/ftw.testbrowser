from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.pages import editbar
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests import IS_PLONE_4
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import nondefault_browsing

import re
import six


@all_drivers
class TestEditBar(BrowserTestCase):

    def setUp(self):
        super(TestEditBar, self).setUp()
        self.folder = create(Builder('folder').titled(u'The Folder'))

    @nondefault_browsing
    def test_visible(self, browser):
        browser.open()
        self.assertFalse(editbar.visible(browser=browser))

        self.grant('Manager')
        browser.login().open()
        self.assertTrue(editbar.visible(browser=browser))

    @nondefault_browsing
    def test_contentviews(self, browser):
        self.grant('Manager')
        browser.login().open()
        self.assertIn('Contents', editbar.contentviews(browser=browser))
        self.assertIn('View', editbar.contentviews(browser=browser))
        self.assertIn('Sharing', editbar.contentviews(browser=browser))

    @nondefault_browsing
    def test_contentview(self, browser):
        self.grant('Manager')
        browser.login().open()
        link = editbar.contentview('Contents', browser=browser)
        self.assertEqual('a', link.tag)
        self.assertEqual(
            self.portal.absolute_url() + '/folder_contents',
            link.attrib['href'].split('?')[0])

    @nondefault_browsing
    def test_contentview_not_found(self, browser):
        self.grant('Manager')
        browser.login().open()
        with self.assertRaises(NoElementFound) as cm:
            editbar.contentview('Nonexisting View', browser=browser)

        msg_start = (
            "Empty result set:"
            " editbar.contentview('Nonexisting View',"
            " browser=<ftw.browser.core.Browser instance>) did not match any nodes."
            "\nVisible content views: ['Contents',")
        self.assertRegexpMatches(
            str(cm.exception),
            '^' + re.escape(msg_start))

    @nondefault_browsing
    def test_menus(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        if IS_PLONE_4:
            self.assertEqual([u'State:', 'Add new', 'Display', 'Actions'],
                             editbar.menus(browser=browser))
        else:
            self.assertEqual([u'Add new', 'State:', 'Actions', 'Display', 'Manage portlets'],
                             editbar.menus(browser=browser))

    @nondefault_browsing
    def test_menu(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        if IS_PLONE_4:
            self.assertIn('actionMenu', editbar.menu('Display', browser=browser).classes)
            self.assertIn('actionMenu', editbar.menu('Add new', browser=browser).classes)
        else:
            self.assertEqual('plone-contentmenu-display',
                             editbar.menu('Display', browser=browser).attrib['id'])
            self.assertEqual('plone-contentmenu-factories',
                             editbar.menu('Add new', browser=browser).attrib['id'])
            self.assertEqual('plone-contentmenu-workflow',
                             editbar.menu('State:', browser=browser).attrib['id'])

    @nondefault_browsing
    def test_menu_not_found(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        with self.assertRaises(NoElementFound) as cm:
            editbar.menu('Shapes', browser=browser)

        if IS_PLONE_4:
            self.assertEqual(
                "Empty result set: editbar.menu('Shapes',"
                " browser=<ftw.browser.core.Browser instance>) did not match any nodes."
                "\nVisible menus: ['State:', 'Add new', 'Display', 'Actions'].",
                str(cm.exception))
        else:
            self.assertEqual(
                "Empty result set: editbar.menu('Shapes',"
                " browser=<ftw.browser.core.Browser instance>) did not match any nodes."
                "\nVisible menus: ['Add new', 'State:', 'Actions', 'Display', 'Manage portlets'].",
                str(cm.exception))

    @nondefault_browsing
    def test_menu_options(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        self.assertIn('Summary view', editbar.menu_options('Display', browser=browser))

    @nondefault_browsing
    def test_menu_option(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        link = editbar.menu_option('Display', 'Summary view', browser=browser)
        self.assertEqual('plone-contentmenu-display-summary_view',
                         link.attrib.get('id'))
        self.assertEqual('a', link.tag)

    @nondefault_browsing
    def test_menu_option_not_found(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        with self.assertRaises(NoElementFound) as cm:
            editbar.menu_option('Add new', 'Dog', browser=browser)

        self.assertEqual(
            "Empty result set: editbar.menu_option('Add new', 'Dog',"
            " browser=<ftw.browser.core.Browser instance>)"
            " did not match any nodes."
            "\nOptions in menu 'Add new': ['Collection', 'DXType', 'Event',"
            " 'File', 'Folder', 'Image', 'Link', 'News Item', 'Page', " +
            ("u" if six.PY2 else "") + "'Restrictions\u2026']",
            str(cm.exception))

    @nondefault_browsing
    def test_menu_option_menu_not_found(self, browser):
        self.grant('Manager')
        browser.login().open(self.folder)
        with self.assertRaises(NoElementFound) as cm:
            editbar.menu_option('Shapes', 'Square', browser=browser)

        if IS_PLONE_4:
            self.assertEqual(
                "Empty result set: editbar.menu_option('Shapes', 'Square',"
                " browser=<ftw.browser.core.Browser instance>)"
                " did not match any nodes."
                "\nVisible menus: ['State:', 'Add new', 'Display', 'Actions'].",
                str(cm.exception))
        else:
            self.assertEqual(
                "Empty result set: editbar.menu_option('Shapes', 'Square',"
                " browser=<ftw.browser.core.Browser instance>)"
                " did not match any nodes."
                "\nVisible menus: ['Add new', 'State:', 'Actions', 'Display', 'Manage portlets'].",
                str(cm.exception))

    @nondefault_browsing
    def test_container(self, browser):
        browser.open()
        with self.assertRaises(NoElementFound):
            editbar.container(browser=browser)

        self.grant('Manager')
        browser.login().open()
        self.assertTrue(editbar.container(browser=browser))
