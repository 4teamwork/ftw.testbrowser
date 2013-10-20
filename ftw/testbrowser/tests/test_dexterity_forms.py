from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
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
