from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from ftw.testing import staticuid


@all_drivers
class TestDexterityDataGridWidget(BrowserTestCase):

    @browsing
    @staticuid()
    def test_datagrid_form_fill(self, browser):
        self.grant('Manager')
        browser.login().visit(view='test-z3cform-shopping')

        browser.fill({'Cakes': [
            {'Quantity': '1', 'Cake': u'Cream Cheese Pound Cake'},
            {'Quantity': '2', 'Cake': u'Ultimate Chocolate Cheese Cake',
             'Low-fat': True, 'Reference': create(Builder('page'))},
        ]})
        browser.find('Submit').click()
        self.assertEquals(
            {u'cakes': [
                {u'cake': u'cream-cheese-pound-cake',
                 u'low_fat': False,
                 u'quantity': 1,
                 u'reference': None},
                {u'cake': u'ultimate-chocolate-cheese-cake',
                 u'low_fat': True,
                 u'quantity': 2,
                 u'reference': u'testdatagridformfill000000000001'}]},
            browser.json)
