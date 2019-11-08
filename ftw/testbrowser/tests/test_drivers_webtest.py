from ftw.testbrowser.compat import HAS_ZOPE4
from ftw.testbrowser.interfaces import IDriver
from unittest import skipIf
from unittest import TestCase
from zope.interface.verify import verifyClass


if HAS_ZOPE4:
    from ftw.testbrowser.drivers.webtest import WebtestDriver
else:
    WebtestDriver = None


@skipIf(not HAS_ZOPE4, 'Webtest is not available for Zope 2')
class TestWebtestDriverImplementation(TestCase):

    def test_implements_interface(self):
        verifyClass(IDriver, WebtestDriver)
