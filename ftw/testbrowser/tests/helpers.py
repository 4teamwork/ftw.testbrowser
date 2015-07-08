from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
import os.path


def asset(name, mode='r'):
    return open(os.path.join(os.path.dirname(__file__), 'assets', name), mode)


class register_view(object):

    def __init__(self, view, name):
        self.view = view
        self.name = name

    def __enter__(self):
        self.get_sitemanager().registerAdapter(factory=self.view,
                                               required=(Interface, Interface),
                                               provided=IBrowserView,
                                               name=self.name)

    def __exit__(self, exc_type, exc_value, traceback):
        self.get_sitemanager().unregisterAdapter(factory=self.view,
                                                 required=(Interface, Interface),
                                                 provided=IBrowserView,
                                                 name=self.name)

    def get_sitemanager(self):
        return getGlobalSiteManager()
