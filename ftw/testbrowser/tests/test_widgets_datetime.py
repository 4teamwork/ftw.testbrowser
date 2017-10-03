from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
import transaction


@all_drivers
class TestDatetimeWidget(BrowserTestCase):

    def setUp(self):
        super(TestDatetimeWidget, self).setUp()
        registry = getUtility(IRegistry)
        if 'plone.portal_timezone' in registry:
            registry['plone.portal_timezone'] = 'Europe/Berlin'
            transaction.commit()

    @browsing
    def test_z3cform_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Delivery date': datetime(2010, 12, 22, 10, 30, 0)})
        browser.find('Submit').click()
        self.assertEquals({u'delivery_date': u'2010-12-22T10:30:00'},
                          browser.json)

    @browsing
    def test_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).open()
        factoriesmenu.add('Event')
        browser.fill({'Title': 'Event',
                      'Event Starts': datetime(2010, 5, 3, 23, 30, 0),
                      'Event Ends': datetime(2010, 12, 23, 10, 5, 0)})
        browser.find('Save').click()

        self.assertEquals(['2010-05-03T23:30:00+02:00'],
                          browser.css('li.dtstart').text)
        self.assertEquals(['2010-12-23T10:05:00+01:00'],
                          browser.css('li.dtend').text)
