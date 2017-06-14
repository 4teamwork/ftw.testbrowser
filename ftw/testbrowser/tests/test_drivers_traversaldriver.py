from ftw.testbrowser import browsing
from ftw.testbrowser.drivers.traversaldriver import TraversalDriver
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.testing import TRAVERSAL_TESTING
from ftw.testbrowser.tests import BrowserTestCase
from plone.app.testing import SITE_OWNER_NAME
from zope.interface.verify import verifyClass
import transaction


class TestTraversalDriverImplementation(BrowserTestCase):
    layer = TRAVERSAL_TESTING

    def test_implements_interface(self):
        verifyClass(IDriver, TraversalDriver)

    @browsing
    def test_does_not_require_transaction_commit(self, browser):
        self.portal.setTitle('New Plone Site')
        browser.open()
        self.assertEquals('New Plone Site', browser.css('title').first.text)

    @browsing
    def test_does_not_commit_transactions(self, browser):
        self.assertEquals('Plone site', self.portal.Title())
        browser.login(SITE_OWNER_NAME).open(view='edit')
        browser.fill({'Site title': 'New site title'}).save()

        self.assertEquals('New site title', self.portal.Title())
        transaction.begin()  # reset to last commited state
        self.assertEquals(
            'Plone site', self.portal.Title(),
            'The traversal driver should not commit the transaction.')
