from ftw.testbrowser.drivers.mechdriver import MechanizeDriver
from ftw.testbrowser.interfaces import IDriver
from unittest2 import TestCase
from zope.interface.verify import verifyClass


class TestMechanizeDriverImplementation(TestCase):

    def test_implements_interface(self):
        verifyClass(IDriver, MechanizeDriver)
