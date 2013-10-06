from ftw.browser import browser


def logged_in():
    """If a user is logged in in the current browser session (last request), it
    resturns the user-ID, otherwise ``False``.
    """

    match = browser.css('#user-name')
    if match:
        return match[0].text.strip()
    else:
        return False
