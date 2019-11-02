from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.utils import getFSVersionTuple
from unittest import skipIf


@skipIf(getFSVersionTuple() < (5, 0),
        'The related items widget requires Plone 5 or later')
@all_drivers
class TestRelatedItemsWidget(BrowserTestCase):

    def setUp(self):
        super(TestRelatedItemsWidget, self).setUp()
        self.grant('Manager')

    @browsing
    def test_selecting_object(self, browser):
        foo = create(Builder('document').titled(u'Foo'))
        bar = create(Builder('document').titled(u'Bar'))

        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Documents': (foo, bar)})
        browser.find('Submit').click()
        self.assertEqual({u'documents': [IUUID(foo), IUUID(bar)]},
                         browser.json)

    @browsing
    def test_querying_objects(self, browser):
        doc = create(Builder('document').titled(u'The Document'))

        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')

        self.assertEqual([[IUUID(doc), u'The Document']],
                         browser.find('Documents').query('doc'))
