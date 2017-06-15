from contextlib import contextmanager
from StringIO import StringIO
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
import os.path
import sys


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


@contextmanager
def capture_streams(stdout=None, stderr=None):
    ori_stdout = sys.stdout
    ori_stderr = sys.stderr

    assert not isinstance(ori_stdout, StringIO), 'stdout already captured'
    assert not isinstance(ori_stderr, StringIO), 'stderr already captured'

    if stdout is not None:
        sys.stdout = stdout
    if stderr is not None:
        sys.stderr = stderr

    try:
        yield
    finally:
        if stdout is not None:
            sys.stdout = ori_stdout
        if stderr is not None:
            sys.stderr = ori_stderr
