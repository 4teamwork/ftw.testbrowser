from cssselect.xpath import HTMLTranslator
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.utils import normalize_spaces
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
    'label',
    )


RESULT_SET_TYPES = (types.ListType,
                    types.TupleType,
                    types.GeneratorType,
                    lxml.etree.ElementDepthFirstIterator,
                    lxml.etree.AncestorsIterator,
                    lxml.etree.ElementChildIterator,
                    lxml.etree.SiblingsIterator)


_marker = object()


def wrapped_nodes(func, browser=_marker):
    """A method decorator wrapping the returned results.
    """
    if browser is not _marker:
        def wrapper_method(*args, **kwargs):
            result = func(*args, **kwargs)
            return wrap_nodes(result, browser)

    else:
        def wrapper_method(self, *args, **kwargs):
            browser = getattr(self, 'browser', _marker)
            if browser is _marker and self.__class__.__name__ == 'Browser':
                browser = self
            if browser is _marker:
                raise ValueError(
                    '{1}.{2} uses the wrapped_nodes decorator but does not'
                    ' provide a `self.browser`.'.format(
                        self.__class__.__name__,
                        func.__name__))

            result = func(self, *args, **kwargs)
            return wrap_nodes(result, browser)

    wrapper_method.__name__ = func.__name__
    wrapper_method.__doc__ = func.__doc__
    return wrapper_method


def wrap_nodes(nodes, browser, query_info=None):
    """Wrap one or many nodes.
    """
    if not isinstance(nodes, RESULT_SET_TYPES):
        return wrap_node(nodes, browser)

    result = Nodes(query_info=query_info)
    for node in nodes:
        result.append(wrap_node(node, browser))
    return result


def wrap_node(node, browser):
    """Wrap a single node.
    """

    if node is None:
        return node

    if isinstance(node, NodeWrapper):
        return node

    if node.tag == 'a':
        return LinkNode(node, browser)

    if node.tag == 'form':
        from ftw.testbrowser.form import Form
        return Form(node, browser)

    if node.tag == 'input' and node.attrib.get('type', None) == 'submit':
        from ftw.testbrowser.form import SubmitButton
        return SubmitButton(node, browser)

    if node.tag == 'button' and node.attrib.get('type', None) == 'submit':
        from ftw.testbrowser.form import SubmitButton
        return SubmitButton(node, browser)

    if node.tag == 'input' and node.attrib.get('type', None) == 'file':
        from ftw.testbrowser.form import FileField
        return FileField(node, browser)

    if node.tag == 'select':
        from ftw.testbrowser.form import SelectField
        return SelectField(node, browser)

    if node.tag == 'textarea':
        from ftw.testbrowser.form import TextAreaField
        return TextAreaField(node, browser)

    if node.tag == 'dl':
        return DefinitionListNode(node, browser)

    if node.tag == 'table':
        from ftw.testbrowser.table import Table
        return Table(node, browser)

    if node.tag == 'tr':
        from ftw.testbrowser.table import TableRow
        return TableRow(node, browser)

    if node.tag in ('td', 'th'):
        from ftw.testbrowser.table import TableCell
        return TableCell(node, browser)

    if node.tag in ('colgroup', 'col', 'thead', 'tbody', 'tfoot'):
        from ftw.testbrowser.table import TableComponent
        return TableComponent(node, browser)

    from ftw.testbrowser.widgets.base import WIDGETS
    for widget_klass in WIDGETS:
        if widget_klass.match(NodeWrapper(node, browser)):
            return widget_klass(node, browser)

    return NodeWrapper(node, browser)


class Nodes(list):
    """A list of HTML nodes. This is used as result set when doing queries
    (css / xpath) on the HTML document. It acts as a list.
    """

    def __init__(self, *args, **kwargs):
        if 'query_info' in kwargs:
            self.query_info = kwargs.pop('query_info')
        else:
            self.query_info = None
        super(Nodes, self).__init__(*args, **kwargs)

    @property
    def first(self):
        """The first element of the list.

        :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
        """
        if len(self) == 0:
            raise NoElementFound(query_info=self.query_info)

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
        if len(args) > 0:
            query_info = (self, 'css', args[0])
        else:
            query_info = (self, 'css', args)

        return Nodes(reduce(list.__add__,
                            map(methodcaller('css', *args, **kwargs), self)),
                     query_info=query_info)

    def xpath(self, *args, **kwargs):
        """Find nodes by an *xpath* expression which are within one of the
        nodes in this result set.
        The resulting nodes are merged into a new result set.

        :param xpath_selector: The xpath selector.
        :type xpath_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        if len(args) > 0:
            query_info = (self, 'xpath', args[0])
        else:
            query_info = (self, 'xpath', args)

        return Nodes(reduce(list.__add__,
                            map(methodcaller('xpath', *args, **kwargs), self)),
                     query_info=query_info)

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

    def __init__(self, node, browser):
        if isinstance(node, NodeWrapper):
            node = node.node
        self.node = node
        self._browser = browser

    def __getattr__(self, name):
        result = getattr(self.node, name)
        if name in METHODS_TO_WRAP:
            return wrapped_nodes(result, browser=self.browser)

        elif name in PROPERTIES_TO_WRAP:
            return wrap_nodes(result, self.browser)
        else:
            return result

    def __setattr__(self, name, value):
        if name not in ('node', '_browser'):
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

        if isinstance(repr, unicode):
            repr = repr.encode('utf-8')
        return '<%s:%s>' % (self.__class__.__name__, repr)

    def __unicode__(self):
        return str(self).decode('utf-8')

    @property
    def browser(self):
        """The current browser instance.
        """
        return self._browser

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
        translator = HTMLTranslator()

        for css in css_selector.split(','):
            css = css.strip()
            if css.startswith('>'):
                # The translator does not allow leading '>', because it is not
                # context sensitive.
                xpath.append(translator.css_to_xpath(
                    css[1:], prefix='self::*/'))
            else:
                xpath.append(translator.css_to_xpath(
                    css, prefix='descendant-or-self::'))

        xpath_expr = ' | '.join(xpath)

        query_info = (self, 'css', css_selector)
        return self.xpath(xpath_expr, query_info=query_info)

    def xpath(self, xpath_selector, query_info=None):
        """Find nodes within this node by a *css* selector.

        :param css_selector: The CSS selector.
        :type css_selector: string
        :returns: Object containg matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        query_info = query_info or (self, 'xpath', xpath_selector)
        nsmap = self.node.getroottree().getroot().nsmap
        return wrap_nodes(self.node.xpath(xpath_selector, namespaces=nsmap),
                          self.browser,
                          query_info=query_info)

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
            translator = HTMLTranslator()
            xpath = translator.css_to_xpath(css, prefix='')

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
            yield wrap_node(element, self.browser), attribute, link, pos

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

        HTML line breaks (`<br />`) are turned into a single newlineand
        paragraphs (`<p></p>`) and with two newlines, although the end
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
        # reduce multiple spaces in a row to one
        text = re.sub(' +', ' ', text)
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
           Use property :py:func:`ftw.testbrowser.nodes.NodeWrapper.text`
           instead.

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

    @property
    def innerHTML(self):
        """The unmodified HTML content of the current node.
        The HTML-Tag of the current node is not included.

        :returns: HTML
        :rtype: unicode
        """

        # Remove the current opening and closing tag
        # from outerHTML to get innerHTML.

        html = self.outerHTML
        html = html.split('>', 1)[1]
        html = '<'.join(html.split('<')[:-1])
        return html

    @property
    def normalized_innerHTML(self):
        """The whitespace-normalized HTML content of the current node.
        The HTML-Tag of the current node is not included.
        All series of whitespaces (including non-breaking spaces) are replaced
        with a single space.

        :returns: HTML
        :rtype: unicode
        """
        return normalize_spaces(self.innerHTML)

    @property
    def outerHTML(self):
        """The whitespace-normalized HTML of the current node and its children.
        The HTML-Tag of the current node is included.

        :returns: HTML
        :rtype: unicode
        """
        return lxml.html.tostring(self.node,
                                  encoding='utf8',
                                  with_tail=False).decode('utf-8')

    @property
    def normalized_outerHTML(self):
        """The whitespace-normalized HTML of the current node and its children.
        The HTML-Tag of the current node is included.
        All series of whitespaces (including non-breaking spaces) are replaced
        with a single space.

        :returns: HTML
        :rtype: unicode
        """
        return normalize_spaces(self.outerHTML)


class LinkNode(NodeWrapper):
    """Wrapps an `<a>` node.
    """

    def click(self):
        """Clicks on the link, which opens the target in the current browser.
        """
        self.browser.open(self.attrib['href'], referer=True)


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
