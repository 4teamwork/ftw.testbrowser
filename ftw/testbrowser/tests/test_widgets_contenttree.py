from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.tests import BrowserTestCase
from ftw.testbrowser.tests.alldrivers import all_drivers
from plone.app.testing import SITE_OWNER_NAME
from Products.CMFPlone.utils import getFSVersionTuple
from unittest import skipIf


@skipIf(getFSVersionTuple() >= (5, 0),
        'The content tree widget is only for Plone 4.3')
@all_drivers
class TestContentTreeWidget(BrowserTestCase):

    def setUp(self):
        super(TestContentTreeWidget, self).setUp()
        self.grant('Manager')

    @browsing
    def test_selecting_object(self, browser):
        foo = create(Builder('document').titled(u'Foo'))
        bar = create(Builder('document').titled(u'Bar'))

        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Documents': (foo, bar)})
        browser.find('Submit').click()
        self.assertEqual({u'documents': [u'/foo',
                                         u'/bar']},
                         browser.json)

    @browsing
    def test_querying_objects(self, browser):
        create(Builder('document').titled(u'The Document'))

        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')

        self.assertEqual([['/plone/the-document', 'The Document']],
                         browser.find('Documents').query('doc'))
