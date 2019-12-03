from ftw.testbrowser.compat import HAS_ZOPE4
from ftw.testbrowser.interfaces import IDriver
from unittest import skipIf
from unittest import TestCase
from zope.interface.verify import verifyClass


if not HAS_ZOPE4:
    from ftw.testbrowser.drivers.mechdriver import MechanizeDriver
else:
    MechanizeDriver = None


@skipIf(HAS_ZOPE4, 'Mechanize is not available for Zope 4')
class TestMechanizeDriverImplementation(TestCase):

    def test_implements_interface(self):
        verifyClass(IDriver, MechanizeDriver)
