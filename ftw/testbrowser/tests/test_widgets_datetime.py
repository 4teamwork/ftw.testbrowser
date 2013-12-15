from datetime import datetime
from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestBrowserZ3CForms(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    @browsing
    def test_datefield_form_fill(self, browser):
        browser.login().visit(view='test-z3cform-shopping')
        browser.fill({'Delivery date': datetime(2010, 12, 22, 10, 30, 00)})
        browser.find('Submit').click()
        self.assertEquals({u'delivery_date': u'2010-12-22T10:30:00'}, browser.json)
