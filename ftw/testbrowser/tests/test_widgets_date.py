from datetime import date
from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from unittest2 import TestCase


class TestDateWidget(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_z3cform_datefield_formfill(self, browser):
        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Day of payment': date(2015, 10, 22)})
        browser.find('Submit').click()
        self.assertEquals({u'day_of_payment': u'2015-10-22'},
                          browser.json)
