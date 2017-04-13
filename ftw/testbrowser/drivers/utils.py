from functools import partial


def remembering_for_reload(func):
    """Decorator which stores the method call into ``self.previous_make_request``
    so that it can be called later for a reload.
    The arguments are stored too, so that ``self.previous_make_request()`` can
    be used without arguments for having the same request.
    """
    def wrapper(self, *args, **kwargs):
        wrappedfunc = getattr(self, func.__name__)
        self.previous_make_request = partial(wrappedfunc, *args, **kwargs)
        return func(self, *args, **kwargs)
    return wrapper
