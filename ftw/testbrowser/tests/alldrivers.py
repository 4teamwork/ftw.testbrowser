from ftw.testbrowser.core import LIB_MECHANIZE
from ftw.testbrowser.core import LIB_REQUESTS
from ftw.testbrowser.testing import MECHANIZE_TESTING
from ftw.testbrowser.testing import REQUESTS_TESTING
from unittest2 import skip
import sys


def all_drivers(testcase):
    """Decorator for test classes so that the tests are run against all drivers.
    """

    module = sys.modules[testcase.__module__]
    drivers = (('Mechanize', MECHANIZE_TESTING, LIB_MECHANIZE),
               ('Requests', REQUESTS_TESTING, LIB_REQUESTS))
    testcase._testbrowser_abstract_testclass = True

    for postfix, layer, constant in drivers:
        name = testcase.__name__ + postfix
        custom = {'layer': layer,
                  '__module__': testcase.__module__,
                  '_testbrowser_abstract_testclass': False}

        subclass = type(name, (testcase,), custom)
        for attrname in dir(subclass):
            method = getattr(subclass, attrname, None)
            func = getattr(method, 'im_func', None)
            if getattr(func, '_testbrowser_skip_driver', None) == constant:
                reason = func._testbrowser_skip_reason
                setattr(subclass, attrname, skip(reason)(method))

        setattr(module, name, subclass)

    setattr(module, 'load_tests', load_tests)
    return testcase


def skip_driver(driver_constant, reason):
    """When the test class is for "all_drivers", the "skip_driver" decorator
    allows to skip one test method for one driver.
    """
    def decorator(func):
        func._testbrowser_skip_driver = driver_constant
        func._testbrowser_skip_reason = reason
        return func
    return decorator


def load_tests(loader, tests, _):
    """The load_tests function is copied into each test using the all_drivers
    decorator, so that it can filter out the original base class from the test
    discover while keeping it in the globals so that superclass calls keep
    working.
    """
    result = []

    for test_suite in tests:
        if not tuple(test_suite):
            # empty
            continue

        test_class = type(tuple(test_suite)[0])
        if getattr(test_class, '_testbrowser_abstract_testclass', False):
            # skip abstract class
            continue

        result.append(test_suite)
    return loader.suiteClass(result)
