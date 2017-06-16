from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import newSecurityManager
from ftw.testbrowser.drivers.utils import isolate_globalrequest
from ftw.testbrowser.drivers.utils import isolate_securitymanager
from ftw.testbrowser.drivers.utils import isolate_sitehook
from ftw.testbrowser.drivers.utils import isolated
from ftw.testbrowser.testing import DEFAULT_TESTING
from ftw.testbrowser.tests import BrowserTestCase
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from Products.CMFPlone.Portal import PloneSite
from zope.component.hooks import getSite
from zope.component.hooks import setSite
from zope.globalrequest import getRequest
from zope.globalrequest import setRequest


class TestIsolation(BrowserTestCase):
    layer = DEFAULT_TESTING

    def test_isolate_globalrequest(self):
        setRequest(self.layer['request'])

        with isolate_globalrequest():
            self.assertIsNone(None, getRequest())
            setRequest('bar')

        self.assertEquals(self.layer['request'], getRequest())

    def test_decorator_isolates_globalrequest(self):
        setRequest(self.layer['request'])

        @isolated
        def foo():
            self.assertIsNone(None, getRequest())
            setRequest('bar')
            return 'Foo'

        self.assertEquals('Foo', foo())
        self.assertEquals(self.layer['request'], getRequest())

    def test_isolate_sitehook(self):
        setSite(self.layer['portal'])

        with isolate_sitehook():
            self.assertIsNone(None, getSite())
            setSite(PloneSite('fakesite'))

        self.assertEquals(self.layer['portal'], getSite())

    def test_decorator_isolates_sitehook(self):
        setSite(self.layer['portal'])

        @isolated
        def foo():
            self.assertIsNone(None, getSite())
            setSite(PloneSite('fakesite'))
            return 'Foo'

        self.assertEquals('Foo', foo())
        self.assertEquals(self.layer['portal'], getSite())

    def test_isolate_securitymanager(self):
        newSecurityManager(self.layer['portal'], TEST_USER_ID)
        security_manager = getSecurityManager()

        with isolate_securitymanager():
            self.assertIsNone(None, getSecurityManager())
            newSecurityManager(self.layer['portal'], SITE_OWNER_NAME)

        self.assertEquals(security_manager, getSecurityManager())

    def test_decorator_isolates_security_manager(self):
        newSecurityManager(self.layer['portal'], TEST_USER_ID)
        security_manager = getSecurityManager()

        @isolated
        def foo():
            self.assertIsNone(None, getSecurityManager())
            newSecurityManager(self.layer['portal'], SITE_OWNER_NAME)
            return 'Foo'

        self.assertEquals('Foo', foo())
        self.assertEquals(security_manager, getSecurityManager())
