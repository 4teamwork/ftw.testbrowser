from contextlib import contextmanager
from plone.app.layout.viewlets.interfaces import IHtmlHeadLinks
from plone.app.layout.viewlets.interfaces import IScripts
from Products.CMFPlone.resources.browser.scripts import ScriptsView
from Products.CMFPlone.resources.browser.styles import StylesView
from zope.browser.interfaces import IBrowserView
from zope.component import getGlobalSiteManager
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.viewlet.interfaces import IViewlet
import os


ENV_NAME = 'TESTBROWSER_DISABLE_RESOURCE_REGISTRIES'


class DisabledScriptsView(ScriptsView):

    def update(self):
        pass

    def render(self):
        return ''


class DisabledStylesView(StylesView):

    def update(self):
        pass

    def render(self):
        return ''


@contextmanager
def disabled_resource_registries():
    """In Plone 5 testing, the resources are cooked on each test, which is very time consuming.
    The same test is 4-5x slower on Plone 5 than on Plone 4.
    Since the testbrowser does not care about CSS and JavaScript, we can simply patch these
    viewlets to be no longer executed, making the tests a lot faster.
    """

    if os.environ.get(ENV_NAME, '').lower() == 'false':
        yield
        return

    sm = getGlobalSiteManager()

    registrations = [
        (DisabledScriptsView,
         [Interface, IDefaultBrowserLayer, IBrowserView, IScripts],
         IViewlet,
         'plone.resourceregistries.scripts'),

        (DisabledStylesView,
         [Interface, IDefaultBrowserLayer, IBrowserView, IHtmlHeadLinks],
         IViewlet,
         'plone.resourceregistries.styles'),
    ]

    for registration in registrations:
        sm.registerAdapter(*registration)

    try:
        yield
    finally:
        for registration in registrations:
            sm.unregisterAdapter(*registration)
