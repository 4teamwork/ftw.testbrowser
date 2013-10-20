import re


class BrowserException(Exception):
    """ftw.testbrowser exception base class.
    """

    def __init__(self):
        message = re.sub(r'\s+', ' ', self.__doc__.strip())
        Exception.__init__(self, message)


class BrowserNotSetUpException(BrowserException):
    """The browser is not set up properly.
    Use the browser as a context manager with the "with" statement.
    """


class FormFieldNotFound(BrowserException):
    """Could not find a form field.
    """

    def __init__(self, label_or_name, labels=None):
        if labels:
            label_advice = ' Fields: "%s"' % '", "'.join(labels)
        else:
            label_advice = ''

        Exception.__init__(self, 'Could not find form field: "%s".%s' % (
                label_or_name, label_advice))


class AmbiguousFormFields(BrowserException):
    """Trying to change fields over multiple forms is not possible.
    """


class NoElementFound(BrowserException):
    """Empty result set has no elements.
    """
