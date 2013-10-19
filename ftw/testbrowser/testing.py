from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class BrowserLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import ftw.testbrowser.tests.views
        xmlconfig.file('configure.zcml',
                       ftw.testbrowser.tests.views,
                       context=configurationContext)


BROWSER_FIXTURE = BrowserLayer()
BROWSER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BROWSER_FIXTURE,),
    name="ftw.testbrowser:functional")
