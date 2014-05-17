from ftw.testbrowser import browser as default_browser
from ftw.testbrowser.utils import normalize_spaces


def logged_in(browser=default_browser):
    """If a user is logged in in the current browser session (last request), it
    resturns the user-ID, otherwise ``False``.
    """

    match = browser.css('#user-name')
    if match:
        return match[0].text.strip()
    else:
        return False


def view(browser=default_browser):
    """Returns the view, taken from the template class, of the current page.

    """
    for cls in browser.css('body').first.classes:
        if cls.startswith('template-'):
            return cls.split('-', 1)[1]
    return None


def portal_type(browser=default_browser):
    """Returns the current content type, extracted from the body css classes.
    """
    for cls in browser.css('body').first.classes:
        if cls.startswith('portaltype-'):
            return cls.split('-', 1)[1]
    return None


def view_and_portal_type(browser=default_browser):
    """Returns a tuple of the view and the content type, both taken from the
    body css classes.
    """
    return (view(browser=browser), portal_type(browser=browser))


def first_heading(browser=default_browser):
    """Returns the whitespace-normalized first heading of the current page.
    """
    first_heading = browser.css('.documentFirstHeading').first
    return normalize_spaces(first_heading.text_content())


def document_description(browser=default_browser):
    """Returns the whitespace-normalized document description of the
    current page or None.
    """
    nodes = browser.css('.documentDescription')
    if len(nodes) == 0:
        return None
    return normalize_spaces(nodes.first.text_content())
