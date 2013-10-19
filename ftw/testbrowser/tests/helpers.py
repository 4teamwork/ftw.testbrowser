from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView


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
