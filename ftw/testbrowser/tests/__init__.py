from ftw.testbrowser import browser
from ftw.testbrowser import LIB_TRAVERSAL
from plone.app.testing import FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import pkg_resources
import transaction


IS_PLONE_4 = pkg_resources.get_distribution('Plone').version[:2] == '4.'


class BrowserTestCase(TestCase):

    def setUp(self):
        self.portal = self.layer['portal']

    def transactions_enabled(self):
        """Returns a boolean indicating whether we are currently using
        transactions.
        We are not using transactions when the layer is not a functional
        testing layer.
        We are not using transactions when the traversal driver is active,
        since the idea of the traversal driver is that it can be used without
        transactions and it therefore does not commit anything nor rely on
        a commited transaction.
        """
        if not isinstance(self.layer, FunctionalTesting):
            return False
        if browser.default_driver == LIB_TRAVERSAL:
            return False
        return True

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        self.maybe_commit_transaction()

    def sync_transaction(self):
        """Especially with the requests driver we sometimes need to sync
        the transaction in order to get hold of new transactions committed
        on another thread or on another connection.
        """
        if self.transactions_enabled():
            transaction.begin()

    def maybe_commit_transaction(self):
        """Commit the transaction when transactions are enabled, in order to
        have a change made in the testing connection available in the next
        request.
        """
        if self.transactions_enabled():
            transaction.commit()
