from ftw.testbrowser.testing import DX_TYPES_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class DxFunctionalTestCase(TestCase):
    layer = DX_TYPES_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
