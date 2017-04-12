from datetime import date
from ftw.testbrowser import browsing
from ftw.testbrowser.tests import FunctionalTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME


@all_drivers
class TestDateWidget(FunctionalTestCase):

    @browsing
    def test_z3cform_datefield_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Day of payment': date(2015, 10, 22)})
        browser.find('Submit').click()
        self.assertEquals({u'day_of_payment': u'2015-10-22'},
                          browser.json)
