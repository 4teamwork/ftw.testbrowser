from ftw.testbrowser.parser import TestbrowserHTMLParser
from zope.interface.declarations import implementedBy
import lxml
import re


def normalize_spaces(text):
    return re.sub(r'[\s\xa0]{1,}', ' ', text).strip()


def parse_html(html):
    return lxml.html.parse(html, TestbrowserHTMLParser())


def copy_docs_from_interface(klass):
    """Class decorator for copying the method documentation from the only
    implemented interface to the actual method function documentation.
    This makes it possible to autodoc it in sphinx documentation.
    """

    iface, = implementedBy(klass)
    for name, spec in iface.namesAndDescriptions():
        getattr(klass, name).im_func.__doc__ = spec.__doc__

    return klass
