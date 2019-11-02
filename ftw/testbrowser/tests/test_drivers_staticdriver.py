from ftw.testbrowser.drivers.staticdriver import StaticDriver
from ftw.testbrowser.interfaces import IDriver
from unittest import TestCase
from zope.interface.verify import verifyClass


class TestStaticDriverImplementation(TestCase):

    def test_implements_interface(self):
        verifyClass(IDriver, StaticDriver)
