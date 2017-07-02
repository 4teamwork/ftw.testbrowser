from ftw.testbrowser import browser as default_browser
from ftw.testbrowser.exceptions import NoElementFound
from ftw.testbrowser.queryinfo import QueryInfo
from ftw.testbrowser.utils import normalize_spaces


def visible(browser=default_browser):
    """Returns ``True`` when the editbar is visible on the current page.

    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: ``True`` when the editbar is visible, ``False`` when it is not.
    :rtype: boolean
    """
    return len(browser.css('#edit-bar')) > 0


def contentviews(browser=default_browser):
    """Returns the text labels of all visible content views.

    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: A list of the labels of the visible content views.
    :rtype: list of str
    """
    return container(browser=browser).css('.contentViews >li >a').text


@QueryInfo.build
def contentview(label, browser=default_browser, query_info=None):
    """Finds and returns a content view link node by its label.

    :param label: The label of the contentview to find.
    :type label: string
    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: The link node (``<a>``) of the content view.
    :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
    :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
    """
    contentviews_node = container(browser=browser).css('.contentViews').first
    link = contentviews_node.find(label)
    if link is None:
        query_info.add_hint('Visible content views: {!r}.'.format(
            contentviews(browser=browser)))
        raise NoElementFound(query_info)
    else:
        return link


def menus(browser=default_browser):
    """Returns the text labels of all visible menus in the edit bar.

    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: A list of the labels of the visible menus.
    :rtype: list of str
    """
    return map(
        lambda text: text.rstrip(u'\u2026'),  # Add new...
        container(browser=browser).css(
            '#contentActionMenus .actionMenuHeader > a > span:first-child').text)


@QueryInfo.build
def menu(label, browser=default_browser, query_info=None):
    """Finds a menu by label and returns its ``<dl class="actionMenu">`` node.

    :param label: The label of the menu to find.
    :type label: string
    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: The menu container node.
    :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
    :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
    """
    menus_node = container(browser=browser).css('#contentActionMenus').first
    label = normalize_spaces(label).rstrip(u'\u2026')
    for span in menus_node.css('.actionMenuHeader > a > span:first-child'):
        if normalize_spaces(span.text_content()).rstrip(u'\u2026') == label:
            return span.parent('.actionMenu')

    query_info.add_hint('Visible menus: {!r}.'.format(menus(browser=browser)))
    raise NoElementFound(query_info)


def menu_options(menu_label, browser=default_browser):
    """Returns the labels of the options of a menu.

    :param menu_label: The label of the menu to find.
    :type menu_label: string
    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: A list of the labels of the visible menus.
    :rtype: list of str
    """
    menu_container = menu(menu_label, browser=browser)
    return menu_container.css('.actionMenuContent a .subMenuTitle').text


@QueryInfo.build
def menu_option(menu_label, option_label, browser=default_browser,
                query_info=None):
    """Returns the link node (``<a>``) of an option in a menu.

    :param menu_label: The label of the menu.
    :type menu_label: string
    :param menu_label: The label of the option to find in the menu.
    :type menu_label: string
    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: The option link node.
    :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
    :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
    """

    menu_container = menu(menu_label, browser=browser, query_info=query_info)
    option_label = normalize_spaces(option_label)
    for link in menu_container.css('.actionMenuContent a'):
        if normalize_spaces(link.text_content()) == option_label:
            return link

    query_info.add_hint('Options in menu {!r}: {!r}'.format(
        menu_label,
        menu_options(menu_label, browser=browser)))
    raise NoElementFound(query_info)


def container(browser=default_browser):
    """Returns the editbar container node or raises a ``NoElementFound``
    exception.

    :param browser: The browser instance to operate with. Uses the global singleton
      default browser by default.
    :type browser: :py:class:`ftw.testbrowser.core.Browser`
    :returns: The ``#edit-bar`` container node.
    :rtype: :py:class:`ftw.testbrowser.nodes.NodeWrapper`
    :raises: :py:exc:`ftw.testbrowser.exceptions.NoElementFound`
    """
    return browser.css('#edit-bar').first
