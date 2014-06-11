from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING
from plone.app.testing import PLONE_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase


class TestArchetypesFileUploadWidget(TestCase):

    layer = PLONE_FUNCTIONAL_TESTING

    @browsing
    def test_filling_file_upload_widget_by_label(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'The file',
                      'File': ('file data', 'file.txt')}).submit()

        browser.find('file.txt').click()
        self.assertEquals('file data', browser.contents)


class TestDexterityFileUploadWidget(TestCase):

    layer = PLONE_APP_CONTENTTYPES_FUNCTIONAL_TESTING

    @browsing
    def test_filling_file_upload_widget_by_label(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('File')
        browser.fill({'Title': 'The file',
                      'File': ('file data', 'file.txt')}).save()

        browser.find('file.txt').click()
        self.assertEquals('file data', browser.contents)
