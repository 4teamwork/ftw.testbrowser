from ftw.testbrowser.compat import HAS_ZOPE4
from ftw.testbrowser.drivers.requestsdriver import RequestsDriver
from ftw.testbrowser.drivers.staticdriver import StaticDriver


#: Constant for choosing the requests library (actual requests)
LIB_REQUESTS = RequestsDriver.LIBRARY_NAME

#: Constant for choosing the static driver.
LIB_STATIC = StaticDriver.LIBRARY_NAME

DRIVER_FACTORIES = {
    RequestsDriver.LIBRARY_NAME: RequestsDriver,
    StaticDriver.LIBRARY_NAME: StaticDriver,
}

if not HAS_ZOPE4:
    from ftw.testbrowser.drivers.traversaldriver import TraversalDriver
    from ftw.testbrowser.drivers.mechdriver import MechanizeDriver

    #: Constant for choosing the mechanize library (interally dispatched requests)
    LIB_TRAVERSAL = TraversalDriver.LIBRARY_NAME
    #: Constant for choosing the mechanize library (interally dispatched requests)
    LIB_MECHANIZE = MechanizeDriver.LIBRARY_NAME
    LIB_WEBTEST = None

    DRIVER_FACTORIES.update({
        TraversalDriver.LIBRARY_NAME: TraversalDriver,
        MechanizeDriver.LIBRARY_NAME: MechanizeDriver,
    })

else:
    from ftw.testbrowser.drivers.webtest import WebtestDriver

    LIB_WEBTEST = WebtestDriver.LIBRARY_NAME
    LIB_TRAVERSAL = None
    LIB_MECHANIZE = None

    DRIVER_FACTORIES.update({
        WebtestDriver.LIBRARY_NAME: WebtestDriver,
    })
