from ftw.testbrowser import browser as default_browser
from ftw.testbrowser.nodes import wrap_nodes
from operator import itemgetter


def titles(browser=default_browser):
    """Returns all titles of the objects listed on the folder contents view.

    :param browser: A browser instance. (Default: global browser)
    :returns: Titles of objects
    :rtype: list of strings
    """
    return title_cells(browser=browser).text


def title_cells(browser=default_browser):
    """Returns all the cell of the title column.

    :param browser: A browser instance. (Default: global browser)
    :returns: Cells of the title column.
    :rtype: list of cell objects
    """
    cells = map(itemgetter(column_title_by_name('title', browser=browser)),
                dicts(browser=browser, as_text=False))
    return wrap_nodes(cells, browser=browser)


def dicts(browser=default_browser, **kwargs):
    """Returns the folder contents table rows as dicts, as described
    in :py:func:`ftw.testbrowser.table.Table.dicts`.
    It removes the select-all header row.

    :param browser: A browser instance. (Default: global browser)
    :returns: List of rows, represented as dicts.
    :rtype: list of dicts
    """
    return table(browser=browser).dicts(head_offset=1, **kwargs)


def select(*objects):
    """Selects the checkboxes on one or more rows by objects.

    :param titles: List of Plone objects to select.
    """
    select_rows(map(row_by_object, objects))


def select_by_title(*titles):
    """Selects the checkboxes on one or more rows by the title of
    the objects.

    :param titles: Titles for objects to select.
    :type titles: list of strings
    """
    select_rows(map(row_by_title, titles))


def select_by_path(*paths):
    """Selects the checkboxes on one or more rows by the path of
    the objects.

    :param titles: Paths for objects to select.
    :type titles: list of strings
    """
    select_rows(map(row_by_path, paths))


def select_rows(rows):
    """Select the checkboxes of set of rows.

    :param rows: A list of row objects.
    :type rows: list of :py:func:`ftw.testbrowser.table.TableRow`.
    """
    for row in rows:
        checkbox = row.css('input[type=checkbox]').first
        checkbox.set('checked', '')


def row_by_title(title, browser=default_browser):
    """Returns the row for an object by its title.

    :param title: The title of the object.
    :type title: string
    :param browser: A browser instance. (Default: global browser)
    :returns: The row node.
    :rtype: :py:class:`ftw.testbrowser.table.TableRow`
    """
    cells = filter(lambda cell: cell.text == title,
                   title_cells(browser=browser))

    if len(cells) == 0:
        raise ValueError('No row with title "{0}" found.'.format(title))

    elif len(cells) == 1:
        return cells[0].row

    else:
        urls = map(lambda cell: cell.css('a').first.attrib['href'], cells)
        raise ValueError(
            'More than one row with title "{0}" found: {1}'.format(
                title, urls))


def row_by_object(obj, browser=default_browser):
    """Returns the row for an object.

    :param obj: The object to look for.
    :param browser: A browser instance. (Default: global browser)
    :returns: The row node.
    :rtype: :py:class:`ftw.testbrowser.table.TableRow`
    """
    path = '/'.join(obj.getPhysicalPath())
    return row_by_path(path, browser=browser)


def row_by_path(path, browser=default_browser):
    """Returns the row for an object by its path.

    :param obj: The path of the object to look for.
    :type obj: string
    :param browser: A browser instance. (Default: global browser)
    :returns: The row node.
    :rtype: :py:class:`ftw.testbrowser.table.TableRow`
    """
    rows = rows_by_path(browser=browser)
    if path in rows:
        return rows[path]
    else:
        raise ValueError(
            'The object with path "{0}" is not visible.'
            ' Visible objects: {1}'.format(
                path, rows.keys()))


def table(browser=default_browser):
    """The folder contents table node.

    :param browser: A browser instance. (Default: global browser)
    :returns: The folder contents table node.
    :rtype: :py:class:`ftw.testbrowser.table.Table`
    """
    selector = 'body.template-folder_contents #content table.listing'
    return browser.css(selector).first


def form(browser=default_browser):
    """The folder contents form node.

    :param browser: A browser instance. (Default: global browser)
    :returns: The folder contents form node.
    :rtype: :py:class:`ftw.testbrowser.form.Form`
    """
    return browser.css('form[name=folderContentsForm]').first


def selected_paths(browser=default_browser):
    """Returns the paths of checkboxes currently selected.

    :param browser: A browser instance. (Default: global browser)
    :returns: paths of selected checkboxes
    :rtype: tuple of strings
    """
    return tuple(form(browser=browser).values['paths:list'])


def rows_by_path(browser=default_browser):
    result = {}
    for row in table(browser=browser).body_rows:
        path = row.css('input[type=checkbox]').first.attrib['value']
        result[path] = row
    return result


def column_title_by_name(name, browser=default_browser):
    mapping = dict(map(lambda th: (th.attrib.get('id'), th.text),
                       table(browser=browser).head_rows.css('th.column')))
    return mapping['foldercontents-{0}-column'.format(name)]
