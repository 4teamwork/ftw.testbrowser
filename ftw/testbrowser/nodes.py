from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.utils import normalize_spaces
from lxml.cssselect import CSSSelector
from operator import methodcaller
import lxml.etree
import re
import types


METHODS_TO_WRAP = (
    'find_class',
    'findall',
    'getparent',
    'iter',
    'iterancestors',
    'iterchildren',
    'iterdescendants',
    'iterfind',
    'itersiblings',
    'xpath',
    )


PROPERTIES_TO_WRAP = (
    'body',
    )


RESULT_SET_TYPES = (types.ListType,
                    types.TupleType,
                    types.GeneratorType,
                    lxml.etree.ElementDepthFirstIterator,
                    lxml.etree.AncestorsIterator,
                    lxml.etree.ElementChildIterator,
                    lxml.etree.SiblingsIterator)


_marker = object()


def wrapped_nodes(func):
    """A method decorator wrapping the returned results.
    """

    def wrapper_method(*args, **kwargs):
        result = func(*args, **kwargs)
        return wrap_nodes(result)

    wrapper_method.__name__ = func.__name__
    return wrapper_method


def wrap_nodes(nodes):
    """Wrap one or many nodes.
    """
    if not isinstance(nodes, RESULT_SET_TYPES):
        return wrap_node(nodes)

    result = Nodes()
    for node in nodes:
        result.append(wrap_node(node))
    return result


def wrap_node(node):
    """Wrap a single node.
    """

    if node is None:
        return node

    if isinstance(node, NodeWrapper):
        return node

    if node.tag == 'a':
        return LinkNode(node)

    if node.tag == 'form':
        from ftw.testbrowser.form import Form
        return Form(node)

    if node.tag == 'input' and node.attrib.get('type', None) == 'submit':
        from ftw.testbrowser.form import SubmitButton
        return SubmitButton(node)

    if node.tag == 'textarea':
        from ftw.testbrowser.form import TextAreaField
        return TextAreaField(node)

    if node.tag == 'dl':
        return DefinitionListNode(node)

    return NodeWrapper(node)


class Nodes(list):

    @property
    def first(self):
        if len(self) == 0:
            raise NoElementFound()

        return self[0]

    def text_content(self):
        return map(methodcaller('text_content'), self)

    def normalized_text(self):
        return map(methodcaller('normalized_text'), self)

    def css(self, css_selector):
        return self.xpath(CSSSelector(css_selector).path)

    def xpath(self, *args, **kwargs):
        return Nodes(reduce(list.__add__,
                            map(methodcaller('xpath', *args, **kwargs), self)))

    def find(self, *args, **kwargs):
        return Nodes(node for node
                     in map(methodcaller('find', *args, **kwargs), self)
                     if node is not None).remove_duplicates()

    def getparents(self):
        return Nodes(map(methodcaller('getparent'), self)).remove_duplicates()

    def remove_duplicates(self):
        keep = []
        remove = []
        for node in self:
            if node in keep:
                remove.append(node)
            else:
                keep.append(node)

        for node in remove:
            self.remove(node)

        return self


class NodeWrapper(object):

    def __init__(self, node):
        self.node = node

    def __getattr__(self, name):
        result = getattr(self.node, name)
        if name in METHODS_TO_WRAP:
            return wrapped_nodes(result)

        elif name in PROPERTIES_TO_WRAP:
            return wrap_nodes(result)
        else:
            return result

    def __cmp__(self, other):
        return cmp(self.node, getattr(other, 'node', _marker))

    def __repr__(self):
        attribs = ', '.join(['%s="%s"' % (key, value)
                            for key, value in self.attrib.items()])
        if self.text and self.text.strip():
            repr = ', '.join((self.tag, attribs, 'text:"%s"' % self.text))
        else:
            repr = ', '.join((self.tag, attribs))
        return '<%s:%s>' % (self.__class__.__name__, repr)

    @property
    def browser(self):
        from ftw.testbrowser import browser
        return browser

    def css(self, css_selector):
        return self.xpath(CSSSelector(css_selector).path)

    def iterlinks(self, *args, **kwargs):
        for element, attribute, link, pos in self.node.iterlinks(
            *args, **kwargs):
            yield wrap_node(element), attribute, link, pos

    def find(self, text):
        return self.browser.find(text, within=self)

    def contains(self, other):
        return other.within(self)

    def within(self, container):
        return container in tuple(self.iterancestors())

    def normalized_text(self):
        return normalize_spaces(self.text_content())

    @property
    def classes(self):
        """A list of css-classes of this element.
        """
        if not self.attrib.get('class', None):
            return []
        else:
            return re.split(r'\s', self.attrib['class'].strip())


class LinkNode(NodeWrapper):

    def click(self):
        self.browser.open(self.attrib['href'])


class DefinitionListNode(NodeWrapper):

    def keys(self):
        return self.css('>dt')

    def values(self):
        return self.css('>dd')

    def items(self):
        return zip(self.keys(), self.values())

    @property
    def terms(self):
        return self.keys().normalized_text()

    @property
    def definitions(self):
        return self.values().normalized_text()

    def items_text(self):
        return zip(self.terms, self.definitions)
