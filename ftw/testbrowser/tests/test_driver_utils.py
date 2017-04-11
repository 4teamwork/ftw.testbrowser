from ftw.testbrowser.drivers.utils import isolate_globalrequest
from ftw.testbrowser.drivers.utils import isolated
from ftw.testbrowser.testing import DEFAULT_TESTING
from ftw.testbrowser.tests import FunctionalTestCase
from zope.globalrequest import getRequest
from zope.globalrequest import setRequest


class TestIsolation(FunctionalTestCase):
    layer = DEFAULT_TESTING

    def test_decorator_isolates_globalrequest(self):
        setRequest(self.layer['request'])

        @isolated
        def foo():
            self.assertIsNone(None, getRequest())
            setRequest('bar')
            return 'Foo'

        self.assertEquals('Foo', foo())
        self.assertEquals(self.layer['request'], getRequest())

    def test_isolate_globalrequest(self):
        setRequest(self.layer['request'])

        with isolate_globalrequest():
            self.assertIsNone(None, getRequest())
            setRequest('bar')

        self.assertEquals(self.layer['request'], getRequest())
