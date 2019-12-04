from ftw.builder.content import register_dx_content_builders
from ftw.builder.testing import BUILDER_LAYER
from ftw.builder.testing import functional_session_factory
from ftw.builder.testing import set_builder_session_factory
from ftw.testbrowser import MECHANIZE_BROWSER_FIXTURE
from ftw.testbrowser import REQUESTS_BROWSER_FIXTURE
from ftw.testbrowser import TRAVERSAL_BROWSER_FIXTURE
from ftw.testbrowser import WEBTEST_BROWSER_FIXTURE
from ftw.testbrowser.compat import HAS_ZOPE4
from ftw.testing import FTWIntegrationTesting
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PLONE_ZSERVER
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2
from Products.CMFPlone.utils import getFSVersionTuple
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

        if HAS_ZOPE4:
            import Products.SiteErrorLog
            self.loadZCML(package=Products.SiteErrorLog)

        import ftw.testbrowser.tests
        xmlconfig.file('profiles/dxtype.zcml',
                       ftw.testbrowser.tests,
                       context=configurationContext)

        import ftw.testbrowser.tests.views
        xmlconfig.file('configure.zcml',
                       ftw.testbrowser.tests.views,
                       context=configurationContext)

        z2.installProduct(app, 'Products.DateRecurringIndex')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ftw.testbrowser.tests:dxtype')
        applyProfile(portal, 'plone.app.contenttypes:default')
        applyProfile(portal, 'collective.z3cform.datagridfield:default')
        if getFSVersionTuple() < (5, 0):
            applyProfile(portal, 'plone.formwidget.autocomplete:default')
        register_dx_content_builders(force=True)


BROWSER_FIXTURE = BrowserLayer()

TRAVERSAL_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           TRAVERSAL_BROWSER_FIXTURE),
    name='ftw.testbrowser:functional:traversal')

TRAVERSAL_INTEGRATION_TESTING = FTWIntegrationTesting(
    bases=(BROWSER_FIXTURE,
           TRAVERSAL_BROWSER_FIXTURE),
    name='ftw.testbrowser:integration:traversal')

MECHANIZE_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           MECHANIZE_BROWSER_FIXTURE),
    name='ftw.testbrowser:functional:mechanize')

REQUESTS_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           PLONE_ZSERVER,
           REQUESTS_BROWSER_FIXTURE),
    name='ftw.testbrowser:functional:requests')

WEBTEST_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,
           set_builder_session_factory(functional_session_factory),
           PLONE_ZSERVER,
           WEBTEST_BROWSER_FIXTURE),
    name='ftw.testbrowser:functional:webtest')


if HAS_ZOPE4:
    DEFAULT_TESTING = WEBTEST_TESTING
else:
    DEFAULT_TESTING = MECHANIZE_TESTING
