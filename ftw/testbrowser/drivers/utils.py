from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SecurityManagement import setSecurityManager
from contextlib import contextmanager
from functools import partial
from functools import wraps
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.component.hooks import setSite
import pkg_resources


try:
    pkg_resources.get_distribution('zope.globalrequest')
except pkg_resources.DistributionNotFound:
    HAS_GLOBALREQUEST = False
else:
    HAS_GLOBALREQUEST = True
    from zope.globalrequest import getRequest
    from zope.globalrequest import setRequest


def remembering_for_reload(func):
    """Decorator which stores the method call into ``self.previous_make_request``
    so that it can be called later for a reload.
    The arguments are stored too, so that ``self.previous_make_request()`` can
    be used without arguments for having the same request.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        wrappedfunc = getattr(self, func.__name__)
        self.previous_make_request = partial(wrappedfunc, *args, **kwargs)
        return func(self, *args, **kwargs)
    return wrapper


def isolated(func):
    """Decorator for isolating the environment within a function.
    Isolates:
    - globalrequest
    - site hook
    - security manager
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with isolate_globalrequest(), \
             isolate_sitehook(), \
             isolate_securitymanager():
                return func(*args, **kwargs)
    return wrapper


@contextmanager
def isolate_globalrequest():
    """Context manager for global request isolation.
    """
    if not HAS_GLOBALREQUEST:
        yield
        return

    request = getRequest()
    setRequest(None)
    try:
        yield
    finally:
        setRequest(request)


@contextmanager
def isolate_sitehook():
    """Context manager for global site hook isolation.
    """
    site = getSite()
    setSite(None)
    try:
        yield
    finally:
        setSite(site)


@contextmanager
def isolate_securitymanager():
    """Context manager for security manager isolation.
    """
    manager = getSecurityManager()
    noSecurityManager()
    try:
        yield
    finally:
        setSecurityManager(manager)


def ensure_plone_catalog_queue_processed():
    """In order for marking added objects as safe in plone.protect,
    we must ensure that the catalog is processed and the data structures
    actually are created at this point.
    """
    try:
        from Products.CMFCore.indexing import processQueue
    except ImportError:
        pass
    else:
        processQueue()


def ensure_plone_protect_changes_marked_as_save(request):
    """Event handler for marking all objects touched on this request
    as save writes.
    """
    if not is_plone_protect_autocsrf_enabled():
        return

    from plone.protect.auto import safeWrite
    from plone.transformchain.interfaces import ITransform

    transform = getMultiAdapter((None, request),
                                ITransform,
                                name='plone.protect.autocsrf')
    for obj in transform._registered_objects():
        safeWrite(obj, request)


def is_plone_protect_autocsrf_enabled():
    """Returns whether we expect the plone.protect auto CSRF protection
    to be enabled.
    It is usually enabled in Plone 5.
    """

    try:
        dist = pkg_resources.get_distribution('plone.protect')
    except pkg_resources.DistributionNotFound:
        # plone.protect is not installed
        return False
    else:
        # auto CSRF is enabled in plone.protect>=3
        return int(dist.version.split('.')[0]) >= 3
