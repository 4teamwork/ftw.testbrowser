from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import plone
from ftw.testbrowser.pages import statusmessages
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
from plone.app.dexterity.behaviors.exclfromnav import IExcludeFromNavigation
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase


class TestDexterityForms(TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    @browsing
    def test_tinymce_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': 'The page',
                      'Text': '<p>The body text.</p>'}).find('Save').click()
        self.assertEquals('The body text.',
                          browser.css('#content-core').first.normalized_text())

    @browsing
    def test_save_add_form(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': 'The page'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals('http://nohost/plone/the-page/view', browser.url)

    @browsing
    def test_fill_umlauts(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': u'F\xf6lder'}).save()
        statusmessages.assert_no_error_messages()
        self.assertEquals(u'F\xf6lder', plone.first_heading())

    @browsing
    def test_changing_checkbox_values(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': u'Page',
                      'Exclude from navigation': True}).save()
        statusmessages.assert_no_error_messages()
        self.assertTrue(IExcludeFromNavigation(browser.context).exclude_from_nav)

        browser.find('Edit').click()
        browser.fill({'Title': 'New Title',
                             'Exclude from navigation': False}).save()
        statusmessages.assert_no_error_messages()
        self.assertFalse(IExcludeFromNavigation(browser.context).exclude_from_nav)

    @browsing
    def test_checkbox_values_are_preserved(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Page')
        browser.fill({'Title': u'Page',
                      'Exclude from navigation': True}).save()
        statusmessages.assert_no_error_messages()
        self.assertTrue(IExcludeFromNavigation(browser.context).exclude_from_nav)

        browser.find('Edit').click()
        browser.fill({'Title': 'New Title'}).save()
        statusmessages.assert_no_error_messages()
        self.assertTrue(IExcludeFromNavigation(browser.context).exclude_from_nav)
