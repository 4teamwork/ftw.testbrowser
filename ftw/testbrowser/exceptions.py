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
            message = '\n'.join(
                ['Empty result set: {} did not match any nodes.'.format(
                    query_info.render_call())] + query_info.get_hints())
            Exception.__init__(self, message)
        else:
            super(NoElementFound, self).__init__()


class ZServerRequired(BrowserException):
    """The requests driver can only be used with a running ZServer.
    Use the `plone.app.testing.PLONE_ZSERVER` testing layer.
    """


class NoWebDAVSupport(BrowserException):
    """The current testbrowser driver does not support webdav requests.
    """


class OptionsNotFound(BrowserException):
    """Could not find the options for a widget.
    """

    def __init__(self, field_label, options, labels=None):
        if labels:
            label_advice = ' Options: "%s"' % '", "'.join(labels)
        else:
            label_advice = ''

        msg = 'Could not find options %s for field "%s".%s' % (
            str(options), field_label, label_advice)
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


class RedirectLoopException(BrowserException):
    """The server returned a redirect response that would lead to
    an infinite redirect loop.
    """

    def __init__(self, url):
        message = re.sub(r'\s+', ' ', self.__doc__.strip())
        message += '\nURL: {}'.format(url)
        Exception.__init__(self, message)
        self.url = url


class HTTPError(IOError):
    """The request has failed.

    :ivar status_code: The status code number
    :type status_code: ``int``
    :ivar status_reason: The status reason.
    :type status_reason: ``string``
    """

    def __init__(self, status_code, status_reason):
        self.status_code = status_code
        self.status_reason = status_reason
        super(HTTPError, self).__init__('{} {}'.format(
            status_code, status_reason))


class HTTPClientError(HTTPError):
    """The request caused a client error with status codes 400-499.

    :ivar status_code: The status code number, e.g. ``404``
    :type status_code: ``int``
    :ivar status_reason: The status reason, e.g. ``"Not Found"``
    :type status_reason: ``string``
    """


class HTTPServerError(HTTPError):
    """The request caused a server error with status codes 500-599.

    :ivar status_code: The status code number, e.g. ``500``
    :type status_code: ``int``
    :ivar status_reason: The status reason, e.g. ``"Internal Server Error"``
    :type status_reason: ``string``
    """


class InsufficientPrivileges(HTTPClientError):
    """This exception is raised when Plone responds that the user has
    insufficient privileges for performing that request.

    Plone redirects the user to a "require_login" script when the user has
    not enough privileges (causing an internal Unauthorized exception to be
    raised).

    When a user is logged in, the "require_login" script will render a page
    with the title "Insufficient Privileges".
    For anonymous users, the login form is rendered.
    Both cases cause the testbrowser to raise an InsufficientPrivileges
    exception.

    This exception can be disabled with by disabling the ``raise_http_errors``
    option.
    """
