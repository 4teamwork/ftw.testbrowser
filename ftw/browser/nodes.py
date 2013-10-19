from ftw.browser.exceptions import NoElementFound
from lxml.cssselect import CSSSelector
import lxml.etree
import types


METHODS_TO_WRAP = (
    'find',
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

    else:
        return NodeWrapper(node)


class Nodes(list):

    @property
    def first(self):
        if len(self) == 0:
            raise NoElementFound()

        return self[0]


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

    def __eq__(self, other):
        return self.node == getattr(other, 'node', _marker)

    @property
    def browser(self):
        from ftw.browser import browser
        return browser

    def css(self, css_selector):
        return self.xpath(CSSSelector(css_selector).path)

    def iterlinks(self, *args, **kwargs):
        for element, attribute, link, pos in self.node.iterlinks(*args, **kwargs):
            yield wrap_node(element), attribute, link, pos


class LinkNode(NodeWrapper):

    def click(self):
        self.browser.open(self.attrib['href'])
