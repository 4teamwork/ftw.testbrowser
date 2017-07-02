from functools import wraps
import inspect


class QueryInfo(object):
    """A QueryInfo object holds information about which query was executed
    in order to have better exception messages when content cannot be found.

    For example, a QueryInfo object records a ``node.css('.foo')`` call so
    that we can tell the user which expression did not match.
    The QueryInfo object can be enriched with additional information.
    """

    def __init__(self, function, args, kwargs):
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.hints = []

    @classmethod
    def build(klass, function):
        argspec = inspect.getargspec(function)
        if 'query_info' not in argspec.args and not argspec.keywords:
            raise NameError(
                'QueryInfo.build wrapped functions must accept a'
                ' query_info argument or arbitrary keyword'
                ' arguments (**kwargs).')

        @wraps(function)
        def wrapper(*args, **kwargs):
            if 'query_info' in kwargs:
                pass
            elif 'query_info' in argspec.args and  \
                 len(args) > argspec.args.index('query_info'):
                pass
            else:
                kwargs['query_info'] = klass(function, args[:], kwargs.copy())
            return function(*args, **kwargs)
        return wrapper

    def render(self):
        """Render the query info object with the function call and the hints.

        :returns: The method call.
        :rtype: string
        """
        return '\n'.join([self.render_call()] + self.hints)

    def add_hint(self, text):
        """Append a hint as text to the query info object.
        When an error is rendered using the query info object, the hint
        will be shown too.

        :param text: The hint text.
        :type text: string
        """
        self.hints.append(text)

    def get_hints(self):
        """Returns a list of hints.

        :returns: List of current hints.
        :rtype: list of string
        """
        return self.hints

    def render_call(self):
        """render the function call made to the wrapped function and return
        the string with the context, the name of the function and the
        arguments.

        :returns: The method call.
        :rtype: string
        """
        argument_names = inspect.getargspec(self.function).args
        positional_arguments = list(self.args)
        if argument_names[0] == 'self':
            # we have an instance method
            context = repr(positional_arguments.pop(0))

        elif len(positional_arguments) > 0 \
             and type(positional_arguments[0]) is type:
            # we have a class method
            context = positional_arguments.pop(0).__name__

        else:
            # we have a module function
            context = inspect.getmodule(self.function).__name__.split('.')[-1]

        keyword_names = []
        keyword_values = []
        keyword_order = argument_names + sorted(self.kwargs.keys())
        for name, value in sorted(
                self.kwargs.items(),
                key=lambda item: keyword_order.index(item[0])):
            keyword_names.append(name)
            keyword_values.append(value)

        return '{}.{}{}'.format(
            context,
            self.function.__name__,
            inspect.formatargspec(
                map(repr, positional_arguments) + keyword_names,
                None, None,
                keyword_values))
