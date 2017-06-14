from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.pages import statusmessages
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testbrowser.tests.helpers import asset
from plone.app.testing import SITE_OWNER_NAME


@all_drivers
class TestDexterityFileUploadWidget(BrowserTestCase):

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

        self.sync_transaction()
        browser.open(browser.context, view='@@images/image.gif')
        self.assertEquals('image/gif', browser.headers.get('Content-Type'))
