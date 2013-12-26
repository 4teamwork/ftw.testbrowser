from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.utils import normalize_spaces
from lxml.cssselect import CSSSelector
from lxml.cssselect import css_to_xpath
from operator import attrgetter
from operator import methodcaller
from zope.deprecation import deprecate
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
    wrapper_method.__doc__ = func.__doc__
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

    if node.tag == 'table':
        from ftw.testbrowser.table import Table
        return Table(node)

    if node.tag == 'tr':
        from ftw.testbrowser.table import TableRow
        return TableRow(node)

    if node.tag in ('td', 'th'):
        from ftw.testbrowser.table import TableCell
        return TableCell(node)

    if node.tag in ('colgroup', 'col', 'thead', 'tbody', 'tfoot'):
        from ftw.testbrowser.table import TableComponent
        return TableComponent(node)

    from ftw.testbrowser.widgets.base import WIDGETS
    for widget_klass in WIDGETS:
        if widget_klass.match(NodeWrapper(node)):
            return widget_klass(node)

    return NodeWrapper(node)


class Nodes(list):
    """A list of HTML nodes. This is used as result set when doing queries
    (css / xpath) on the HTML document. It acts as a list.
    """

    @property
    def first(self):
        """The first element of the list.

        :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
        """
        if len(self) == 0:
            raise NoElementFound()

        return self[0]

    @property
    def first_or_none(self):
        """The first element of the list or ``None`` if the list is empty.
        """
        if len(self) > 0:
            return self[0]
        else:
            return None

    def text_content(self):
        """Returns a list with the text content of each node of this result
        set.

        :returns: A list of the `text_content` of each node.
        :rtype: list

        .. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.text_content`
        """
        return map(methodcaller('text_content'), self)

    @deprecate('Nodes.normalized_text is deprecated in favor of Nodes.text')
    def normalized_text(self, recursive=True):
        """Returns a list with the *normalized* text content of each node of
        this result set.

        :param recursive: Set to ``False`` for not including text of
            contained tags.
        :type recursive: Boolean (default: ``True``)
        :returns: A list of the `normalized_text` of each node.
        :rtype: list

        .. deprecated:: 1.3.1
           Use property :py:func:`ftw.testbrowser.nodes.Nodes.text` instead.

        .. seealso::
          :py:func:`ftw.testbrowser.nodes.NodeWrapper.normalized_text`
        """
        return map(methodcaller('normalized_text', recursive=recursive), self)

    @property
    def text(self):
        """A list of all ``text`` properties of this result set.

        .. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.text`

        :returns: A list of text
        :rtype: list of string
        """
        return map(attrgetter('text'), self)

    @property
    def raw_text(self):
        """A list of all ``raw_text`` properties of this result set.

        .. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.raw_text`

        :returns: A list of raw text
        :rtype: list of string
        """
        return map(attrgetter('raw_text'), self)

    def css(self, *args, **kwargs):
        """Find nodes by a *css* expression which are within one of the nodes
        in this result set.
        The resulting nodes are merged into a new result set.

        :param xpath_selector: The xpath selector.
        :type xpath_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return Nodes(reduce(list.__add__,
                            map(methodcaller('css', *args, **kwargs), self)))

    def xpath(self, *args, **kwargs):
        """Find nodes by an *xpath* expression which are within one of the
        nodes in this result set.
        The resulting nodes are merged into a new result set.

        :param xpath_selector: The xpath selector.
        :type xpath_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return Nodes(reduce(list.__add__,
                            map(methodcaller('xpath', *args, **kwargs), self)))

    def find(self, *args, **kwargs):
        """Find a elements by text. The elements are searched within each node
        of the current result set.

        The method looks for:
        - a link with this text (normalized, including subelements' texts)
        - a field which has a label with this text
        - a button which has a label with this text

        :param text: The text to be looked for.
        :type text: string
        :returns: A list of the parent of each node in the current result set.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return Nodes(node for node
                     in map(methodcaller('find', *args, **kwargs), self)
                     if node is not None).remove_duplicates()

    def getparents(self):
        """Returns a list of each node's parent.

        :returns: The parent of each node of the current result set.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return Nodes(map(methodcaller('getparent'), self)).remove_duplicates()

    def __repr__(self):
        return '<Nodes: %s>' % str(list(self))

    def __add__(self, other):
        return Nodes(list(self) + list(other))

    def __radd__(self, other):
        return Nodes(list(other) + list(self))

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
    """`NodeWrapper` is the default wrapper class in which each element will be
    wrapped for use in `ftw.testbrowser`. It wraps the elements returned by
    `lxml` and redirects calls if it does not overload them.

    There are more specific node wrapper classes for some elements.
    """

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

    def __setattr__(self, name, value):
        if name != 'node':
            setattr(self.node, name, value)
        else:
            super(NodeWrapper, self).__setattr__(name, value)

    def __cmp__(self, other):
        return cmp(self.node, getattr(other, 'node', _marker))

    def __repr__(self):
        attribs = ', '.join(['%s="%s"' % (key, value)
                             for key, value in self.attrib.items()])

        text = self.raw_text
        if isinstance(text, unicode):
            text = text.encode('utf-8')

        if text and text.strip():
            repr = ', '.join((self.tag, attribs, 'text:"%s"' % text))
        else:
            repr = ', '.join((self.tag, attribs))
        return '<%s:%s>' % (self.__class__.__name__, repr)

    @property
    def browser(self):
        """The current browser instance.
        """
        from ftw.testbrowser import browser
        return browser

    def css(self, css_selector):
        """Find nodes within this node by a *css* selector.

        :param css_selector: The CSS selector.
        :type css_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """

        xpath = []

        # When a direct child is selected (">x"), we need to prefix the xpath
        # expression with "self::" rather than "descendant-or-self::" for not
        # selecting the children of the children.
        # "self::*/div"                 -->   ">div"
        # "descendant-or-self::*/div"   -->   ">div, >* div"
        # "descendant-or-self::div"     -->   "div"
        for css in css_selector.split(','):
            if css.strip().startswith('>'):
                xpath.append(css_to_xpath(css, prefix='self::'))
            else:
                xpath.append(css_to_xpath(css, prefix='descendant-or-self::'))

        xpath_expr = ' | '.join(xpath)
        return self.xpath(xpath_expr)

    @wrapped_nodes
    def xpath(self, xpath_selector):
        """Find nodes within this node by a *css* selector.

        :param css_selector: The CSS selector.
        :type css_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.node.xpath(xpath_selector)

    def parent(self, css=None, xpath=None):
        """Find the nearest parent which (optionally) does match a *css* or
        *xpath* selector.

        If `parent` is called without an argument the first parent is returned.

        Examples:

        .. code:: py

            browser.css('.foo > .bar').first.parent('#content')
            # equals
            browser.css('.foo > .bar').first.parent(xpath='*[@id="content"]')

        :param css: The css selector.
        :type css: string
        :param xpath: The xpath selector.
        :type xpath: string
        :returns: The parent node.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """

        if css and xpath:
            raise ValueError(
                'parent() requires either "css" or "xpath" argument.')
        elif not css and not xpath:
            xpath = '*'

        if css:
            xpath = CSSSelector(css).path.replace('descendant-or-self::', '')

        if not xpath.startswith('ancestor::'):
            xpath = 'ancestor::%s' % xpath

        result = self.xpath(xpath)
        if len(result) > 0:
            return result[-1]
        else:
            return None

    def iterlinks(self, *args, **kwargs):
        """Iterate over all links in this node.
        Each link is represented as a tuple with `node, attribute, link, pos`.
        """
        for element, attribute, link, pos in self.node.iterlinks(
            *args, **kwargs):
            yield wrap_node(element), attribute, link, pos

    def find(self, text):
        """Find an element by text within the current node.

        The method looks for:
        - a link with this text (normalized, including subelements' texts)
        - a field which has a label with this text
        - a button which has a label with this text

        :param text: The text to be looked for.
        :type text: string
        :param within: A node object for limiting the scope of the search.
        :type within: :py:class:`ftw.testbrowser.nodes.NodeWrapper`.
        :returns: A single node object or `None` if nothing matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """
        return self.browser.find(text, within=self)

    def contains(self, other):
        """Test whether the passed `other` node is contained in the current
        node.

        :param other: The other node.
        :type other: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        :returns: `True` when `other` is within `self`.
        :rtype: boolean
        """
        return other.within(self)

    def within(self, container):
        """Test whether the passed `other` node contains the current node.

        :param other: The other node.
        :type other: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        :returns: `True` when `self` is within `other`.
        :rtype: boolean
        """
        return container in tuple(self.iterancestors())

    @property
    def text(self):
        """Returns the whitespace-normalized text of the current node.
        This includes the text of each node within this node recursively.
        All whitespaces are reduced to a single space each, including newlines
        within the text.

        HTML line breaks (`<br />`) are turned into a single newline (`\n`) and
        paragraphs (`<p></p>`) and with two newlines (`\n\n`), although the end
        of the string is stripped.

        For having the original lxml raw text, use ``raw_text``.
        .. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.raw_text`

        :returns: The whitespace normalized text content.
        :rtype: unicode
        """

        def normalize(text):
            # replace all space sequences (including non breaking spaces)
            # with a single space.
            return re.sub(r'[\s\xa0]{1,}', ' ', text)

        def recursive_text(node, include_tail=False):
            if node.tag == 'br':
                yield '\n'

            if node.text:
                yield normalize(node.text)

            for child in tuple(node.iterchildren()):
                yield ''.join(recursive_text(child, include_tail=True))

            if include_tail and node.tail:
                yield normalize(node.tail)

            if node.tag == 'p':
                yield '\n\n'

        text = ''.join(recursive_text(self.node)).strip()
        # strip spaces before and after newlines
        text = re.sub(' *\n *', '\n', text)
        return text

    @property
    def raw_text(self):
        """The original lxml raw text of this node.

        :returns: Original lxml raw text.
        :rtype: unicode
        """
        return self.node.text or u''

    @deprecate('NodeWrapper.normalized_text is deprecated in'
               ' favor of NodeWrapper.text')
    def normalized_text(self, recursive=True):
        """Returns the whitespace-normalized text of the current node.
        This includes the text of each node within this node recurively.
        All whitespaces are reduced to a single space each.

        .. deprecated:: 1.3.1
           Use property :py:func:`ftw.testbrowser.nodes.NodeWrapper.text` instead.

        :param recursive: Set to ``False`` for not including text of
            contained tags.
        :type recursive: Boolean (default: ``True``)
        :returns: The whitespace normalized text content.
        :rtype: unicode
        """
        if recursive:
            return normalize_spaces(self.text_content())
        else:
            return normalize_spaces(self.raw_text or '')

    def text_content(self):
        """Returns the text content of the current node, including the text
        content of each containing node recursively.

        :returns: The text content.
        :rtype: unicode
        """
        return self.node.text_content()

    @property
    def classes(self):
        """A list of css-classes of this element.
        """
        if not self.attrib.get('class', None):
            return []
        else:
            return re.split(r'\s', self.attrib['class'].strip())


class LinkNode(NodeWrapper):
    """Wrapps an `<a>` node.
    """

    def click(self):
        """Clicks on the link, which opens the target in the current browser.
        """
        self.browser.open(self.attrib['href'])


class DefinitionListNode(NodeWrapper):
    """Wrapps a `<dl>` node.
    """

    def keys(self):
        """Returns all `<dt>`-tags which are direct children
        of this definition list.

        :returns: A list of `<dt>`-tags.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.css('>dt')

    def values(self):
        """Returns all `<dd>`-tags which are direct children
        of this definition list.

        :returns: A list of `<dd>`-tags.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.css('>dd')

    def items(self):
        """Returns a mapping (list with tuples) from
        `<dt>`-tags to `<dd>`-tags of this definition list.

        :returns: a dict where the key is the `<dt>`-node and the
          value is the `<dd>`-node.
        :rtype: dict
        """
        return zip(self.keys(), self.values())

    @property
    def terms(self):
        """Returns the normalized text of each `<dt>`-tag of this
        definition list.

        :returns: A list of text of each `<dt>`-node.
        :rtype: list of unicode
        """
        return self.keys().normalized_text()

    @property
    def definitions(self):
        """Returns the normalized text of each `<dd>`-tag of this
        definition list.

        :returns: A list of text of each `<dd>`-node.
        :rtype: list of unicode
        """
        return self.values().normalized_text()

    def items_text(self):
        """Returns a terms (`<dt>`) to definition (`<dd>`) mapping as
        list with tuples, each as normalized text.

        :returns: key is the text of the `<dt>`-node, value is the text of
          the `<dd>`-node.
        :rtype: dict
        """
        return zip(self.terms, self.definitions)

    def text_to_nodes(self):
        """Returns a dict with a mapping of text-terms to `<dd>`-nodes.

        :returns: key is the text of the `<dt>`-node, value is the `<dd>`-node.
        :rtype: dict
        """
        return dict(zip(self.terms, self.values()))
