from ftw.testbrowser.nodes import Nodes
from ftw.testbrowser.nodes import NodeWrapper
from ftw.testbrowser.utils import normalize_spaces
from operator import attrgetter
from operator import itemgetter


def colspan_padded_text(row):
    """Returns a list with the normalized_text of each cell of the ``row``,
    but adds empty padding-cells for cells with a colspan.

    :param node: The row node.
    :type node: :py:class:`ftw.testbrowser.nodes.TableRow`
    :returns: A list of cell texts
    :rtype: list
    """
    def padded_text(cell):
        colspan = int(cell.attrib.get('colspan', '1'))
        return [cell.normalized_text()] * colspan

    return reduce(list.__add__, map(padded_text, row.css('>td, >th')))


class Table(NodeWrapper):
    """Represents a ``table`` tag.
    """

    def find(self, text):
        """Find a cell of this table by text.
        When nothing is found, it falls back to the default ``find`` behavior.

        .. seealso:: :py:func:`ftw.testbrowser.nodes.NodeWrapper.find`

        :param text: The text to be looked for.
        :type text: string
        :returns: A single node object or `None` if nothing matches.
        :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        """
        text = normalize_spaces(text)
        for cell in self.cells:
            if cell.normalized_text() == text:
                return cell

        return super(Table, self).find(text)

    def lists(self, head=True, body=True, foot=True,
              head_offset=0, as_text=True):
        """Returns a list of lists, where each list represents a row and
        contains the texts of the cells.
        Cells with colspan are repeated (padding) so that row lengths
        are equal.

        :param head: Include head rows.
        :type head: boolean (Default: ``True``)
        :param body: Include body rows.
        :type body: boolean (Default: ``True``)
        :param foot: Include foot rows.
        :type foot: boolean (Default: ``True``)
        :param head_offset: Offset for the header for removing header rows.
        :type head_offset: int (Default: ``0``)
        :param as_text: Converts cell values to text.
        :type as_text: Boolean (Default: ``True``)
        :returns: A list of lists of texts.
        :rtype: list
        """
        rows = self.get_rows(head=head, body=body, foot=foot,
                             head_offset=head_offset)
        if as_text:
            return map(colspan_padded_text, rows)
        else:
            return map(attrgetter('cells'), rows)

    def dicts(self, body=True, foot=True,
              head_offset=0, as_text=True):
        """Returns a list of dicts, where each dict is a row (of either
        table body or table foot). The keys of the row dicts are the table
        headings and the values are the cell texts.
        Cells with colspan are repeated.

        :param body: Include body rows.
        :type body: boolean (Default: ``True``)
        :param foot: Include foot rows.
        :type foot: boolean (Default: ``True``)
        :param head_offset: Offset for the header for removing header rows.
        :type head_offset: int (Default: ``0``)
        :param as_text: Converts cell values to text.
        :type as_text: Boolean (Default: ``True``)
        :returns: A list of lists of texts.
        :rtype: list
        """

        titles = self.get_titles(head_offset=head_offset)
        rows = self.lists(head=False, body=body, foot=foot, as_text=as_text)
        return [dict(zip(titles, values)) for values in rows]

    def column(self, index_or_titles, head=True, body=True, foot=True,
               head_offset=0, as_text=True):
        """Returns a list of values of a specific column.
        The column may be identified by its index (integer)
        or by the title (string).

        :param index_or_titles: Index or title of column
        :type index_or_titles: int or string or list of strings
        :param head: Include head rows.
        :type head: boolean (Default: ``True``)
        :param body: Include body rows.
        :type body: boolean (Default: ``True``)
        :param foot: Include foot rows.
        :type foot: boolean (Default: ``True``)
        :param head_offset: Offset for the header for removing header rows.
        :type head_offset: int (Default: ``0``)
        :param as_text: Converts cell values to text.
        :type as_text: Boolean (Default: ``True``)
        :returns: A list of lists of texts.
        :rtype: list
        """
        if isinstance(index_or_titles, int):
            index = index_or_titles
        else:
            titles = self.get_titles(head_offset=head_offset)
            try:
                index = titles.index(index_or_titles)
            except ValueError:
                raise ValueError('Title "{0}" not in titles {1}'.format(
                    index_or_titles, titles))

        return map(itemgetter(index), self.lists(head=head,
                                                 body=body,
                                                 foot=foot,
                                                 head_offset=head_offset,
                                                 as_text=as_text))

    @property
    def titles(self):
        """Returns the titles (thead) of the table.
        If there are multiple table head rows, the cells of the rows are merged
        per column (with newline as separator).

        :returns: A list of table head texts per column.
        :rtype: list
        """
        return self.get_titles()

    def get_titles(self, head_offset=0):
        """Returns the titles (thead) of the table.
        If there are multiple table head rows, the cells of the rows are merged
        per column (with newline as separator).

        :param head_offset: Offset for the header for removing header rows.
        :type head_offset: int (Default: ``0``)
        :returns: A list of table head texts per column.
        :rtype: list
        """
        texts_per_rows = map(colspan_padded_text,
                             self.head_rows[head_offset:])
        texts_per_columns = zip(*texts_per_rows)
        return map('\n'.join, texts_per_columns)

    @property
    def head_rows(self):
        """All heading rows of this table. Heading rows are those rows (``tr``)
        which are within the ``thead`` tag.

        :returns: A list of heading rows.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.filter_unfamiliars(self.css('thead tr'))

    @property
    def foot_rows(self):
        """All footer rows of this table. Footer rows are those rows (``tr``)
        which are within the ``tfoot`` tag.

        :returns: A list of footer rows.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.filter_unfamiliars(self.css('tfoot tr'))

    @property
    def body_rows(self):
        """All body rows of this table.
        Body rows are those rows which are neither heading rows nor footer
        rows.

        .. seealso:: :py:func:`ftw.testbrowser.table.Table.head_rows`,
                     :py:func:`ftw.testbrowser.table.Table.foot_rows`

        :returns: A list of body rows which are part of this table.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        exclude_rows = self.head_rows + self.foot_rows
        return Nodes(filter(lambda node: node not in exclude_rows, self.rows))

    @property
    def rows(self):
        """All rows of this table.

        :returns: A list of rows which are part of this table.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.filter_unfamiliars(self.css('tr'))

    def get_rows(self, head=False, body=False, foot=False, head_offset=0):
        """Returns merged head, body or foot rows.
        Set the keyword arguments to ``True`` for selecting the type of rows.

        :param head: Selects head rows.
        :type head: boolean (Default: ``False``)
        :param body: Selects body rows.
        :type body: boolean (Default: ``False``)
        :param foot: Selects foot rows.
        :type foot: boolean (Default: ``False``)
        :param head_offset: Offset for the header for removing header rows.
        :type head_offset: int (Default: ``0``)
        :returns: A list of rows which are part of this table.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        rows = Nodes()
        if head:
            rows.extend(self.head_rows[head_offset:])
        if body:
            rows.extend(self.body_rows)
        if foot:
            rows.extend(self.foot_rows)
        return rows

    @property
    def cells(self):
        """All cells of this table.

        :returns: A list of cells which are part of this table.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        cells = Nodes()
        for row in self.rows:
            cells.extend(row.cells)
        return cells

    def filter_unfamiliars(self, nodes):
        """Returns all nodes from the ``nodes`` list which are part of this
        table, filtering all other nodes (unfamiliars).

        :param nodes: The list of nodes to filter.
        :type node: :py:class:`ftw.testbrowser.nodes.Nodes`
        :returns: The filtered list of nodes.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return Nodes(filter(lambda node: self.is_familiar(node), nodes))

    def is_familiar(self, node):
        """Returns ``True`` when ``node`` is a component of the this
        table. Returns ``False`` when ``node`` is a table component but is
        part of a nested table.

        :param node: The node to check.
        :type node: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
        :returns: whether ``node`` is part of this table
        :rtype: boolean
        """
        return getattr(node, 'table', None) == self


class TableComponent(NodeWrapper):
    """Represents any component of a table tag.
    This includes: 'colgroup', 'col', 'thead', 'tbody', 'tfoot', 'tr', 'td',
    'th'
    """

    @property
    def table(self):
        """Returns the table of which this button is parent.
        It returns the first table node if it is a nested table.

        :returns: the table node
        :rtype: :py:class:`ftw.testbrowser.table.Table`
        """
        for node in self.iterancestors():
            if node.tag == 'table':
                return node
        return None


class TableRow(TableComponent):
    """Represents a table row (``tr``).
    """

    @property
    def cells(self):
        """The cell nodes of this row.

        :returns: A ``Node`` list of cell nodes.
        :rtype: :py:class:`ftw.testbrowser.nodes.Nodes`
        """
        return self.css('>td, >th')

    def dict(self):
        """Returns this row as dict.
        The keys of the dict are the column titles of the table, the values
        are the cell texts of this row.

        :returns: A dict with the cell texts.
        :rtype: dict
        """
        return dict(zip(self.table.titles, colspan_padded_text(self)))


class TableCell(TableComponent):
    """Represents a table cell (``td`` or ``th``).
    """

    @property
    def row(self):
        """Returns the row (``tr`` node) of this cell.

        :returns: The row node.
        :rtype: :py:class:`ftw.testbrowser.table.TableRow`
        """
        for node in self.iterancestors():
            if node.tag == 'tr':
                return node
        return None
