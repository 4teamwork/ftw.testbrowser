from ftw.testbrowser import browsing
from ftw.testbrowser.compat import HAS_ZOPE4
from ftw.testbrowser.interfaces import IDriver
from ftw.testbrowser.testing import TRAVERSAL_TESTING
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests import IS_PLONE_4
from plone.app.testing import SITE_OWNER_NAME
from plone.registry.interfaces import IRegistry
from unittest import skipIf
from zope.component import getUtility
from zope.interface.verify import verifyClass

import transaction


if not HAS_ZOPE4:
    from ftw.testbrowser.drivers.traversaldriver import TraversalDriver
else:
    TraversalDriver = None


@skipIf(HAS_ZOPE4, 'Traversal is not available for Zope 4')
class TestTraversalDriverImplementation(BrowserTestCase):
    layer = TRAVERSAL_TESTING

    def test_implements_interface(self):
        verifyClass(IDriver, TraversalDriver)

    @browsing
    def test_does_not_require_transaction_commit(self, browser):
        if IS_PLONE_4:
            self.portal.setTitle('New Plone Site')
        else:
            registry = getUtility(IRegistry)
            registry['plone.site_title'] = u'New Plone Site'

        browser.open()
        self.assertEqual('New Plone Site', browser.css('title').first.text)

    @browsing
    def test_does_not_commit_transactions(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        self.assertEqual(['Plone site'], browser.css('title').text)

        browser.open(view='edit')
        browser.fill({'Site title': 'New site title'}).save()

        browser.open()
        self.assertEqual(['New site title'], browser.css('title').text)

        transaction.begin()  # reset to last commited state
        browser.open()
        self.assertEqual(
            ['Plone site'], browser.css('title').text,
            'The traversal driver should not commit the transaction.')
