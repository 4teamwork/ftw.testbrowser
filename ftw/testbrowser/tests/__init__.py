from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class FunctionalTestCase(TestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        if isinstance(self.layer, FunctionalTesting):
            transaction.commit()

    def sync_transaction(self):
        # Especially with the requests driver we sometimes need to sync
        # the transaction in order to get hold of new transactions committed
        # on another thread.
        if isinstance(self.layer, FunctionalTesting):
            transaction.begin()
