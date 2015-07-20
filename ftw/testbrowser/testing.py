from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from zope.configuration import xmlconfig


class BrowserLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, BUILDER_LAYER)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(
            '<configure xmlns="http://namespaces.zope.org/zope">'
            '  <include package="z3c.autoinclude" file="meta.zcml" />'
            '  <includePlugins package="plone" />'
            '  <includePluginsOverrides package="plone" />'
            '</configure>',
            context=configurationContext)

        import ftw.testbrowser.tests.views
        xmlconfig.file('configure.zcml',
                       ftw.testbrowser.tests.views,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.formwidget.autocomplete:default')


BROWSER_FIXTURE = BrowserLayer()
BROWSER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,
           set_builder_session_factory(functional_session_factory)),
    name="ftw.testbrowser:functional")
BROWSER_ZSERVER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           PLONE_ZSERVER),
    name="ftw.testbrowser:functional:zserver")
