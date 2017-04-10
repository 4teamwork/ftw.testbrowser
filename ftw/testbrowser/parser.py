from lxml.html import HtmlElementClassLookup
from lxml.html import HTMLParser
from lxml.html import InputElement


class TestbrowserHTMLParser(HTMLParser):
    """An HTML parser that is configured to return lxml.html Element
    objects.
    """
    def __init__(self, **kwargs):
        super(TestbrowserHTMLParser, self).__init__(**kwargs)
        self.set_element_class_lookup(
            TestbrowserHtmlElementClassLookup({'button': InputElement}))


class TestbrowserHtmlElementClassLookup(HtmlElementClassLookup):

    def __init__(self, classes=None, mixins=None):
        super(TestbrowserHtmlElementClassLookup, self).__init__(None, mixins)
        for key, value in classes.items():
            self._element_classes[key] = value
