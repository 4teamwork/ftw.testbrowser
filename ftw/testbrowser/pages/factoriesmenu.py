from ftw.testbrowser import browser


def menu():
    """Returns the factories menu container node or ``None`` if it is
    not visible.
    """
    nodes = browser.css('#plone-contentmenu-factories')
    if len(nodes) == 0:
        return None
    else:
        return nodes.first


def visible():
    """Returns ``True`` when the factories menu is visible on the current page.
    """
    if menu() is not None:
        return True
    else:
        return False


def add(type_name):
    """Clicks on the add-link in the factories menu for the passed type name.
    The type name is the literal link label.
    This opens the add form for this type.

    :param type_name: The name (label) of the type to add.
    :type type_name: string
    """
    if not visible():
        raise ValueError('Cannot add "%s": no factories menu visible.' % (
                type_name))

    links = menu().css('.actionMenuContent').find(type_name)
    if len(links) == 0:
        raise ValueError('The type "%s" is not addable. Addable types: %s' % (
                type_name,
                ', '.join(addable_types())))

    links.first.click()


def addable_types():
    """Returns a list of addable types. Each addable types is the link label
    in the factories menu.
    """

    if not visible():
        raise ValueError('Factories menu is not visible.')

    return map(str.strip, menu().css('.actionMenuContent a').text_content())
