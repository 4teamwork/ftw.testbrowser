import re


class BrowserException(Exception):
    """ftw.browser exception base class.
    """

    def __init__(self):
        message = re.sub(r'\s+', ' ', self.__doc__.strip())
        Exception.__init__(self, message)


class BrowserNotSetUpException(BrowserException):
    """The browser is not set up properly.
    Use the browser as a context manager with the "with" statement.
    """
