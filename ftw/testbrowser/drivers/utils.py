from contextlib import contextmanager
from functools import partial
from functools import wraps
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
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with isolate_globalrequest():
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
