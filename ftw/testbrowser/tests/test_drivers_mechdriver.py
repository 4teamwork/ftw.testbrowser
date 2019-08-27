from ftw.testbrowser.interfaces import IDriver
from Products.CMFPlone.utils import getFSVersionTuple
from unittest import skipIf
from unittest2 import TestCase
from zope.interface.verify import verifyClass


@skipIf(getFSVersionTuple() >= (5, 2),
        'Mechanize driver not available for Plone >= 5.2')
class TestMechanizeDriverImplementation(TestCase):

    def test_implements_interface(self):
        from ftw.testbrowser.drivers.mechdriver import MechanizeDriver
        verifyClass(IDriver, MechanizeDriver)
