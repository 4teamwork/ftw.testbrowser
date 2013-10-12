from ftw.browser import browser
import re


def logged_in():
    """If a user is logged in in the current browser session (last request), it
    resturns the user-ID, otherwise ``False``.
    """

    match = browser.css('#user-name')
    if match:
        return match[0].text.strip()
    else:
        return False


def view():
    """Returns the view, taken from the template class, of the current page.
    """
    classes = re.split(r'\s', browser.css('body')[0].attrib['class'].strip())
    for cls in classes:
        if cls.startswith('template-'):
            return cls.split('-', 1)[1]
    return None
