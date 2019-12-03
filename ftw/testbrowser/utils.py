from base64 import b64encode
from zope.interface.declarations import implementedBy

import re
import six


def normalize_spaces(text):
    return re.sub(r'[\s\xa0]{1,}', ' ', text).strip()


def copy_docs_from_interface(klass):
    """Class decorator for copying the method documentation from the only
    implemented interface to the actual method function documentation.
    This makes it possible to autodoc it in sphinx documentation.
    """

    iface, = implementedBy(klass)
    for name, spec in iface.namesAndDescriptions():
        if six.PY2:
            getattr(klass, name).__func__.__doc__ = spec.__doc__
        else:
            getattr(klass, name).__doc__ = spec.__doc__

    return klass


def basic_auth_encode(user, password=None):
    # user / password and the return value are of type str
    value = user
    if password is not None:
        value = value + ':' + password
    header = b'Basic ' + b64encode(value.encode('latin-1'))
    if six.PY3:
        header = header.decode('latin-1')
    return header
