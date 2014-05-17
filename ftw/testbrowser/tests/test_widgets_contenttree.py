from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.testing import BROWSER_FUNCTIONAL_TESTING
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles
from unittest2 import TestCase


class TestContentTreeWidget(TestCase):

    layer = BROWSER_FUNCTIONAL_TESTING

    def setUp(self):
        portal = self.layer['portal']
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

    @browsing
    def test_selecting_object(self, browser):
        foo = create(Builder('document').titled('Foo'))
        bar = create(Builder('document').titled('Bar'))

        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')
        browser.fill({'Documents': (foo, bar)})
        browser.find('Submit').click()
        self.assertEquals({u'documents': [u'/foo',
                                          u'/bar']},
                          browser.json)

    @browsing
    def test_querying_objects(self, browser):
        create(Builder('document').titled('The Document'))

        browser.login(SITE_OWNER_NAME).visit(view='test-z3cform-shopping')

        self.assertEquals([['/plone/the-document', 'The Document']],
                          browser.find('Documents').query('doc'))
