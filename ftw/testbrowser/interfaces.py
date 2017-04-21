from zope.interface import Interface


class IBrowser(Interface):

    def open(url_or_object, data=None, view=None):
        """Open the browser and go to an URL or visit the default view of
        an object.

        ``url_or_object`` - an URL (string or unicode) or an object which has
        an ``absolute_url`` returning an URL.

        ``data`` - a dict with form data, where the key is the name of the
        field and the value is the value of the field.

        ``view`` - a view name (string or unicode), which is appended to the
        URL. This is especially useful combined with passing in objects.
        """


class IDriver(Interface):
    """A driver's job is to make requests and to provide informations about
    the response.
    A driver instance is reused for multiple tests / sessions.
    """

    def __init__(browser):
        """A driver is initialized with the browser instance as argument.

        :param browser: The browser object.
        :type browser: :py:class:`ftw.testbrowser.core.Browser`
        """

    def reset():
        """Resets the driver: closes active sessions and resets the
        internal state.
        """

    def make_request(method, url, data=None, headers=None, referer_url=None):
        """Make a request to the url and return the response body as string.

        :param method: The HTTP request method, all uppercase.
        :type method: string
        :param url: A full qualified URL.
        :type url: string
        :param data: A dict with data which is posted using a ``POST`` request,
          or the raw request body as a string.
        :type data: dict or string
        :param headers: A dict with custom headers for this request.
        :type headers: dict
        :param referer_url: The referer URL or ``None``.
        :type referer: string or ``None``
        :returns: Status code, reason and body
        :rtype: tuple: (int, string, string or stream)
        """

    def reload():
        """Reloads the current page by redoing the previous request with
        the same arguments.
        This applies for GET as well as POST requests.

        :raises: :py:exc:`ftw.testbrowser.exceptions.BlankPage`
        :returns: Status code, reason and body
        :rtype: tuple: (int, string, string or stream)
        """

    def get_response_body():
        """Returns the response body of the last response.

        :raises: :py:exc:`ftw.testbrowser.exceptions.BlankPage`
        :returns: Response body
        :rtype: string
        """

    def get_url():
        """Returns the current url, if we are on a page, or None.

        :returns: the current URL
        :rtype: string or None
        """

    def get_response_headers():
        """Returns a dict-like object containing the response headers.
        Returns an empty dict if there is no response.

        :returns: Response header dict
        :rtype: dict
        """

    def get_response_cookies():
        """Retruns a dict-like object containing the cookies set by the
        last response.

        :returns: Response cookies dict
        :rtype: dict
        """

    def append_request_header(name, value):
        """Add a new permanent request header which is sent with every request
        until it is cleared.

        HTTP allows multiple request headers with the same name.
        Therefore this method does not replace existing names.
        Use ``replace_request_header`` for replacing headers.

        Be aware that the ``requests`` library does not support multiple
        headers with the same name, therefore it is always a replace
        for the requests module.

        :param name: Name of the request header
        :type name: string
        :param value: Value of the request header
        :type value: string
        """

    def clear_request_header(name):
        """Removes a permanent header.
        If there is no such header, the removal is silently skipped.

        :param name: Name of the request header as positional argument
        :type name: string
        """

    def cloned(subbrowser):
        """When a browser was cloned, this method is called on each
        driver instance so that the instance can do whatever is needed
        to have a cloned state too.

        :param subbrowser: The cloned subbrowser instance.
        :type subbrowser: :py:class:`ftw.testbrowser.core.Browser`
        """
