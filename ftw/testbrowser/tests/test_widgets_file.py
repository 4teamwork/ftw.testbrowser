from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.tests.helpers import asset
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

    @browsing
    def test_filling_image_upload_widget_by_label(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Image')

        with asset('mario.gif') as mario:
            browser.fill({'Image': (mario.read(), 'mario.gif')}).submit()

        browser.find('Download').click()
        self.assertEquals('attachment; filename="mario.gif"',
                          browser.headers.get('Content-Disposition'))
        self.assertEquals('image/gif',
                          browser.headers.get('Content-Type'))


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

    @browsing
    def test_filling_image_upload_widget_by_label(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Image')

        with asset('mario.gif') as mario:
            browser.fill({'Image': (mario.read(), 'mario.gif')}).save()
        statusmessages.assert_message('Item created')

        browser.open(browser.context, view='@@images/image.gif')
        self.assertEquals('image/gif', browser.headers.get('Content-Type'))
