import re


class BrowserException(Exception):
    """ftw.testbrowser exception base class.
    """

    def __init__(self):
        message = re.sub(r'\s+', ' ', self.__doc__.strip())
        Exception.__init__(self, message)


class BlankPage(BrowserException):
    """The browser is on a blank page.
    """

    def __init__(self, message=''):
        docstr = re.sub(r'\s+', ' ', self.__doc__.strip())
        Exception.__init__(self, ' '.join((docstr, message)).strip())


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

    def __init__(self, query_info=None):
        if query_info is not None:
            message = ('Empty result set: {0}.{1}("{2}") '
                       'did not match any nodes.'.format(*query_info))
            Exception.__init__(self, message)
        else:
            super(NoElementFound, self).__init__()


class ZServerRequired(BrowserException):
    """The `webdav` method can only be used with a running ZServer.
    Use the `plone.app.testing.PLONE_ZSERVER` testing layer.
    """


class OptionsNotFound(BrowserException):
    """Could not find the options for a widget.
    """

    def __init__(self, field_label, options):
        msg = 'Could not find options %s for field "%s".' % (
            str(options), field_label)
        Exception.__init__(self, msg)


class OnlyOneValueAllowed(BrowserException):
    """The field or widget does not allow to set multiple values.
    """


class ContextNotFound(BrowserException):
    """When trying to access a context but the current page has no
    context information, this exception is raised.
    """

    def __init__(self, message=None):
        if message is None:
            message = re.sub(r'\s+', ' ', self.__doc__.strip())
        Exception.__init__(self, message)
