from Products.SiteErrorLog import SiteErrorLog
import logging
import sys


class ExceptionLogger(logging.Handler):
    """When an exception happens while publishing an object, Zope will render
    an error page (500).
    For convenience we want the exception to be printed for a good developer
    experience.
    """

    def __init__(self):
        super(ExceptionLogger, self).__init__()
        self.error_messages = []

    def __enter__(self):
        logging.root.addHandler(self)
        self._ori_rate_period = SiteErrorLog._rate_restrict_period
        # Make sure the rate limit of the error_log does not swallow our
        # exceptions.
        SiteErrorLog._rate_restrict_period = 0
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        SiteErrorLog._rate_restrict_period = self._ori_rate_period
        logging.root.removeHandler(self)

    def filter(self, record):
        if record.name != 'Zope.SiteErrorLog':
            return False

        if not record.msg or not record.msg.strip():
            return False

        return True

    def emit(self, record):
        self.error_messages.append(record.msg)

    def print_captured_exceptions(self):
        if not self.error_messages:
            return

        print >>sys.stderr,  '\n'
        for message in self.error_messages:
            print >>sys.stderr, message
