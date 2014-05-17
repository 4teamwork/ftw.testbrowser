from DateTime import DateTime
from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase


class TestDatetimeWidget(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_z3cform_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Delivery date': datetime(2010, 12, 22, 10, 30, 00)})
        browser.find('Submit').click()
        self.assertEquals({u'delivery_date': u'2010-12-22T10:30:00'},
                          browser.json)

    @browsing
    def test_archetypes_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Event')
        browser.fill({'Title': 'Event',
                      'Event Starts': datetime(2010, 5, 3, 23, 30, 00),
                      'Event Ends': datetime(2010, 12, 23, 10, 05, 00)})
        browser.find('Save').click()

        event = self.layer['portal'].restrictedTraverse('event')
        self.assertEquals(DateTime('2010/05/03 23:30:00'),
                          event.Schema()['startDate'].get(event))
        self.assertEquals(DateTime('2010/12/23 10:05:00'),
                          event.Schema()['endDate'].get(event))
